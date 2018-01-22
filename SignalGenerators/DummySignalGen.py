import numpy as np
import struct
from queue import Empty, Full
import multiprocessing as mp


class DummySignalGen:
    """
    A signal generator which creates a single tone of a specified frequency and volume.
    Used for testing purposes to verify smooth transmission.
    """

    def __init__(self, recq, sendq, args, config):
        self.samplerate = config["fs"]
        self.CHUNK = config["CHUNK"]
        self.buffer = config["playbuffer"]
        self.recq = recq
        self.sendq = sendq
        self.freq = args["freq"]
        self.volume = args["volume"]
        self.terminate = False
        self.lastval = 0

    def data(self):
        # startval = np.arcsin(self.lastval)/(2 * np.pi * self.freq * self.CHUNK/self.samplerate)
        xf = np.linspace(self.lastval + 1 / self.CHUNK, self.lastval + 1 + 1 / self.CHUNK, self.CHUNK)
        self.lastval = xf[-1]
        data = np.sin(xf * 2 * np.pi * self.freq * self.CHUNK / self.samplerate)
        # print(self.lastval, data[0], abs(self.lastval - data[0]))
        # print(data[0], data[1], abs(data[0]- data[1]))

        # data = np.random.randint(0, 2, self.CHUNK)
        # noinspection PyTypeChecker
        data = np.array(data * self.volume * ((2 ** 15) - 1), dtype="int16")
        data = struct.pack('h' * len(data), *data)
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
                if "freq" in message[1]:
                    self.freq = message[1]["freq"]
                if "volume" in message[1]:
                    self.volume = message[1]["volume"]
            elif message[1]["type"] == "terminate":
                self.terminate = True
                if "silent" not in message[1] or not message[1]["silent"]:
                    print("Terminating Signal Gen!")

    @classmethod
    def create_new(cls, seed, config):
        recq = mp.Queue()
        sendq = mp.Queue()
        sgen = cls(recq, sendq, {"seed": seed}, config)
        process = mp.Process(target=sgen.main)
        process.start()
        return sendq, recq
