import struct

import scipy.signal as signal
import numpy as np
import multiprocessing as mp
from queue import Empty, Full
import time
from DeltaConvolution import Convolver

class aChildBasic:

    def __init__(self, seed, recq, sendq, sgenrec, sgensend, args, config):
        self.seed = seed
        self.recq = recq
        self.sendq = sendq
        self.sGen = sgenrec
        self.sGensend = sgensend
        self.data = b''
        self.template = b''

        self.starttime = config["start time"]
        self.terminate = False
        self.convolver = Convolver(np.array([]), np.array([]))

    @staticmethod
    def createNew(seed, args, config):
        recq = mp.Queue()
        sendq = mp.Queue()

        sgenpackage, sgenclass, sgen = config["Signal Generator"]
        signalGen = vars(vars(__import__(sgenpackage, globals(), locals(), [], 0))[sgenclass])[sgen].__func__
        signalgenrecq, signalgensendq = signalGen(seed, args, config)
        aChild = aChildBasic(seed, recq, sendq,signalgenrecq, signalgensendq, args, config)
        childprocess = mp.Process(target=aChildBasic.main, args=(aChild,))
        childprocess.start()

        return recq, sendq


    def main(self):
        while not self.terminate:
            while self.handle_messages():
                pass
            while len(self.data) > len(self.template):
                self.template += self.sGen.get()
            if len(self.data) != 0:
                arraydata = np.array(struct.unpack('h'*(len(self.data)//2), self.data))
                arraytemplate = np.array(struct.unpack('h'*(len(self.template)//2), self.template))
                self.data = b''
                self.template = b''
                if(arraydata.shape[0] > 0):
                    self.analyze(arraydata, arraytemplate)

    def analyze(self, data, template):
        convolved = self.convolver.convolve(data, template).astype(np.float64)
        convolved -= np.average(convolved)
        significance = convolved/np.std(convolved)
        maxsig = np.max(significance)
        result = {"significance":maxsig, "signalnum":self.seed, "time":time.time() - self.starttime}
        self.sendq.put([None, result])

    def handle_messages(self):
        if not self.recq.empty():
            message = self.recq.get_nowait()
            if message[1]["type"] == "terminate":
                self.terminate = True
                self.sGensend.put([None, {"type":"terminate", "silent":True}])
                return 0
            if message[1]["type"] == "new data":
                self.data += message[1]["data"]
                return 1
        else:
            return 0

