import multiprocessing as mp

import matplotlib.pyplot as plt
import numpy as np

from DummySignalGen import DummySignalGen as Dsg

config = {"fs":44100, "CHUNK":44, "playbuffer":10}
args = {"freq":100, "volume":0.1}

signalq = mp.Queue(maxsize=config["playbuffer"])
playrecq = mp.Queue()
playsendq = mp.Queue()
sgrecq = mp.Queue()

args["signalq"] = signalq

SGen = Dsg(sgrecq, signalq, args, config)


#Play = PProc(playrecq, playsendq, args, config)

SignalGen = mp.Process(target=SGen.main)
#PlayProc = mp.Process(target=Play.main)

#PlayProc.start()
SignalGen.start()
data = np.array([], dtype="float32")
vals = []
for i in range(10):
    print(i)
    vals.append(signalq.get())
data = np.append(data, vals)
SignalGen.terminate()
plt.plot(data)
plt.show()


#def terminate():
#    print("terminating")
#    sgrecq.put([None, {"type":"terminate"}])
#    playrecq.put([None, {"type": "terminate"}])


#terminate()

