import atexit
import multiprocessing as mp
import os
import time

from AnalysisHub import AHub
from DataSinkBasic import DSink
from BinarySignalGen import BinarySignalGen as USG
from PlayProc import PlayProc
from RecProc import RecProc as RProc
from logtofile import Logger
from BidirectionalQueue import BQueue

config = {"fs": 10000, "CHUNK": 1000, "playbuffer": 1000, "Minimum Significance": 6, "Significance Factor": 1.5,
          "aChild": ("AChildBasic", "AChildBasic", "create_new"),
          "Signal Generator": ("BinarySignalGen", "BinarySignalGen", "create_new"),
          "Logger": Logger(open("logfile.txt", "w")), "start time": time.time(),
          "initial broadcast duration": 1000}
args = {"seed": 0, "transmitter": False, "volume":0.002}

signalq = mp.Queue()
playrecq = mp.Queue()
sgrecq = mp.Queue()
dsinkq = mp.Queue()
dgenq = BQueue()
playq = mp.Queue(maxsize=config["playbuffer"])
playercontrolq = mp.Queue()

Hub = AHub(sgrecq, signalq, dgenq, dsinkq, args, config)
Rec = RProc(sgrecq, signalq, config)
Sink = DSink(dsinkq, config)
Play = PlayProc(playercontrolq, playq, config)
SGen = USG(sgrecq, playq, args, config)

RecProc = mp.Process(target=Rec.main)
AProc = mp.Process(target=Hub.main)
SProc = mp.Process(target=Sink.main)
PProc = mp.Process(target=Play.main)
SGProc = mp.Process(target=SGen.main)

termqs = [sgrecq, sgrecq, playrecq, dsinkq, playercontrolq]
time.sleep(0.1)

PProc.start()
SGProc.start()
RecProc.start()
AProc.start()
SProc.start()
os.system("taskset -p -c %d %d" % (0, PProc.pid))
os.system("taskset -p -c %d %d" % (0, SGProc.pid))
cpucount = mp.cpu_count()
affinity_string = ",".join([str(i) for i in range(1, cpucount)])
for x in [RecProc, AProc, SProc]:
    os.system("taskset -p -c %s %d" % (affinity_string, x.pid))

dgenq.send([None, {"signals": [0, 1]}])


def terminate():
    print("terminating")
    for q in termqs:
        q.put([None, {"type": "terminate"}])
    time.sleep(0.2)
    print("waited")


atexit.register(terminate)

while True:
    time.sleep(0.1)
