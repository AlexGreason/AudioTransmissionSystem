from RecProc import RecProc as RProc
import atexit
import multiprocessing as mp
import time

from AnalysisHub import AHub
from DataSinkBasic import DSink
from RecProc import RecProc as RProc
from logtofile import Logger
from PlayProc import PlayProc
from GaussSignalGen import GaussSignalGen as BSG
import os

config = {"fs":20000, "CHUNK":1000, "playbuffer":1000, "Minimum Significance": 100, "Significance Factor": 100,
          "aChild":("AChildBasic","AChildBasic", "createNew"),
          "Signal Generator": ("GaussSignalGen", "GaussSignalGen", "createNew"),
          "Logger": Logger(open("logfile.txt", "w")), "start time": time.time(),
          "initial broadcast duration": 1000}
args = {"seed":-1, "transmitter":False, "volume":0.05}

signalq = mp.Queue()
playrecq = mp.Queue()
sgrecq = mp.Queue()
dsinkq = mp.Queue()
dgenq = mp.Queue()
playq = mp.Queue(maxsize=config["playbuffer"])
playercontrolq = mp.Queue()

Hub = AHub(sgrecq, signalq, dgenq, dsinkq, args, config)
Rec = RProc(sgrecq, signalq, args, config)
Sink = DSink(dsinkq, args, config)
Play = PlayProc(playercontrolq, playq, args, config)
SGen = BSG(sgrecq, playq, args, config)


RecProc = mp.Process(target=Rec.main)
AProc = mp.Process(target=Hub.main)
SProc = mp.Process(target=Sink.main)
PProc = mp.Process(target=Play.main)
SGProc = mp.Process(target=SGen.main)

termqs = [sgrecq, playrecq, dsinkq, playercontrolq]
time.sleep(0.1)


PProc.start()
SGProc.start()
RecProc.start()
AProc.start()
SProc.start()
os.system("taskset -p -c %d %d" % (0, PProc.pid))
os.system("taskset -p -c %d %d" % (0, SGProc.pid))
for x in [RecProc, AProc, SProc]:
    os.system("taskset -p -c 1,2,3 %d" % (x.pid))

dgenq.put([None, {"signals": [-1, 0, 1]}])

def terminate():
    print("terminating")
    for q in termqs:
        q.put([None, {"type": "terminate"}])


atexit.register(terminate)

while True:
    time.sleep(0.1)

