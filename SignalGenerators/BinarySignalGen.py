import numpy as np
import struct
from queue import Empty, Full
import multiprocessing as mp


class BinarySignalGen:
    """
    A signal generator which produces random bits
    """

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

    @staticmethod
    def setstate(seed):
        return np.random.RandomState(np.array([seed]).astype(np.uint32)[0])

    def data(self):
        data = ((self.state.random_integers(0, 1, self.CHUNK) * (2 ** 16 - 1) - 2**15) * self.volume).astype(
            "int16")
        data = struct.pack('h' * len(data), *data)
        self.lastval += self.CHUNK
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
    def create_new(seed, args, config):
        recq = mp.Queue()
        sendq = mp.Queue(maxsize=config["playbuffer"])
        sgen = BinarySignalGen(recq, sendq, {"seed": seed, "volume": args["volume"]}, config)
        process = mp.Process(target=sgen.main)
        process.start()
        return sendq, recq
