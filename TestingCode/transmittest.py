import atexit
import multiprocessing as mp
import time

from BinarySignalGen import BinarySignalGen as BSG
from PlayProc import PlayProc as PProc

config = {"fs":44100, "CHUNK":1000, "playbuffer":100, "initial broadcast duration": 1000}
args = {"seed":0, "transmitter":False, "volume":0.05}

signalq = mp.Queue(maxsize=config["playbuffer"])
playrecq = mp.Queue()
sgrecq = mp.Queue()

SGen = BSG(sgrecq, signalq, args, config)
Play = PProc(playrecq, signalq, config)

SignalGen = mp.Process(target=SGen.main)
PlayProc = mp.Process(target=Play.main)

time.sleep(0.1)
PlayProc.start()
SignalGen.start()

def terminate():
    print("terminating")
    sgrecq.put([None, {"type":"terminate"}])
    playrecq.put([None, {"type": "terminate"}])


atexit.register(terminate)

while True:
    time.sleep(0.1)

