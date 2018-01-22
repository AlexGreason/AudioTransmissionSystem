import numpy as np
import struct
from queue import Empty, Full
import time
import multiprocessing as mp

class GaussSignalGen:

    def __init__(self, recq, sendq, args, config):
        self.samplerate = config["fs"]
        self.CHUNK = config["CHUNK"]
        self.buffer = config["playbuffer"]
        self.repeatduration = config["initial broadcast duration"]
        self.recq = recq
        self.sendq = sendq
        self.seed = args["seed"]
        self.state = self.setstate(self.seed)
        self.terminate = False
        self.lastval = 0
        self.currsample = 0
        self.volume = args["volume"]

    def setstate(self, seed):
        return np.random.RandomState(np.array([seed]).astype(np.uint32)[0])

    def data(self):
        if self.seed >= -1 or self.lastval + self.CHUNK <= self.repeatduration:
            data = self.state.random_integers(self.volume * -2**15,self.volume *  2**15-1, self.CHUNK).astype("int16")
            data = struct.pack('h' * len(data), *data)
            self.lastval += self.CHUNK
        else:
            # todo: DOES NOT HANDLE SHORT REPEAT DURATIONS PROPERLY
            # REPEAT DURATION MUST BE AT LEAST CHUNK LENGTH
            data = b''
            remaining = self.repeatduration - self.lastval
            if remaining != 0:
                moredata = self.state.random_integers(self.volume * -2 ** 15, self.volume * 2 ** 15 - 1, remaining).astype(
                    "int16")
                data += struct.pack('h' * len(data), *moredata)
                self.state = self.setstate(self.seed)
            moredata = self.state.random_integers(self.volume * -2 ** 15, self.volume * 2 ** 15 - 1, self.CHUNK - remaining).astype(
                "int16")
            data += struct.pack('h' * len(data), *moredata)
            self.lastval = self.CHUNK - remaining
        return data

    def main(self):
        data = None
        while not self.terminate:
            try:
                while True:
                    if data is None:
                        data = self.data()
                    self.sendq.put(data, timeout=0.01)
                    data = None
            except Full:
                pass
            self.handle_messages()

    def handle_messages(self):
        if not self.recq.empty():
            message = self.recq.get()
            if message[1]["type"] == "new data":
                while not self.sendq.empty():
                    try:
                        self.sendq.get_nowait()
                    except Empty:
                        break
                self.seed = message[1]["seed"]
                self.state = self.setstate(self.seed)
                self.currsample = 0
            elif message[1]["type"] == "terminate":
                self.terminate = True
                print("Terminating Signal Gen!")

    @staticmethod
    def createNew(seed, args, config):
        recq = mp.Queue()
        sendq = mp.Queue()
        sgen = GaussSignalGen(recq, sendq, {"seed":seed, "volume":args["volume"]}, config)
        process = mp.Process(target=sgen.main)
        process.start()
        return sendq, recq