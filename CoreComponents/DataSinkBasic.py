from UpdatingPlot import UpdatingPlot as UP
from queue import Empty, Full
from time import sleep, time

class DSink:

    def __init__(self, recq, args, config):
        self.plot = UP("Significance")
        self.data = {}
        self.recq = recq
        self.terminate = False
        self.starttime = config["start time"]
        self.log = config["Logger"].write_line

    def main(self):
        while not self.terminate:
            i = 0
            while self.handle_messages() and i < 10:
                i += 1
            self.update_plot()

    def handle_messages(self):
        try:
            message = self.recq.get(timeout=0.02)
            if message[1]["type"] == "terminate":
                self.terminate = True
                return False
            if message[1]["type"] == "new data":
                signalnum = message[1]["data"]["signalnum"]
                timestamp = message[1]["data"]["time"]
                print("Behind by " + str(((time() - self.starttime) - timestamp)))
                significance = message[1]["data"]["significance"]
                if signalnum in self.data:
                    self.data[signalnum].append((timestamp, significance))
                else:
                    print("new signal type reporting: " + str(signalnum))
                    self.data[signalnum] = [(timestamp, significance)]
                return True
            if message[1]["type"] == "recieved signal":
                self.log("Recieved signal: " + message[1]["data"]["signalnum"])
                self.data = []
                return True
        except Empty:
            return False

    def update_plot(self):
        xs = []
        ys = []
        for signal in self.data:
            #does not sort by signal number, colors do not necessarily correspond as intended
            data = self.data[signal]
            valx = []
            valy = []
            for val in data:
                valx.append(val[0])
                valy.append(val[1])
            xs.append(valx)
            ys.append(valy)
        if len(xs) != 0:
            self.plot.updateplot(xs, ys, multiplot=True)

