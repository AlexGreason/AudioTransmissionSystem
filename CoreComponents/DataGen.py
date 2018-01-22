

class DGen:

    def __init__(self, recq, sendq, sgenq, args, config):
        self.AHubRec = recq
        self.AHubSend = sendq
        self.SGen = sgenq
        self.transmitter = args["transmitter"]
        self.datafile = open(args["data file"], "rb")
        self.currbyte = self.datafile.read(1)[0]
        self.bitindex = 0
        self.lastrec = None
        self.lastsent = None
        self.terminate = False

    def nextbit(self):
        if self.bitindex == 8:
            self.currbyte = self.datafile.read(1)[0]
            self.bitindex = 0
        bit = ((self.currbyte >> (7 - self.bitindex)) % 2)
        self.bitindex += 1
        return bit

    def main(self):
        while not self.terminate:
            val = self.handle_messages()
            if val:
                self.send_message()

    def send_message(self):
        if self.transmitter:
            val = self.nextbit()
            signals = [2, 3]
            if(self.lastrec != self.lastsent + 2):
                print("TRANSMISSION ERROR")
            self.lastsent = val
        else:
            val = self.lastrec + 2
            signals = [0, 1]
        self.AHubSend.put([None, {"signals":signals}])
        self.SGen.put([None, {"type":"new data", "seed":val}])

    def handle_messages(self):
        message = self.AHubRec.get()
        if message[1]["type"] == "terminate":
            self.terminate = True
            self.SGen.put([None, {"type":"terminate"}])
            return False
        if message[1]["type"] == "new data":
            self.lastrec = message[1]["data"]

