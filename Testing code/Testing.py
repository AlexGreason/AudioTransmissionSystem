import atexit
import multiprocessing as mp
import time

from GaussSignalGen import GaussSignalGen as Bsg
from PlayProc import PlayProc as PProc

config = {"fs":44100, "CHUNK":1000, "playbuffer":100}
args = {"seed":0, "transmitter":False}

signalq = mp.Queue(maxsize=config["playbuffer"])
playrecq = mp.Queue()
sgrecq = mp.Queue()

SGen = Bsg(sgrecq, signalq, args, config)
Play = PProc(playrecq, signalq, args, config)

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

