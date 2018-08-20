class DGen:
    """
    Data Generator. Determines what signal should be sent and what signals should be searched for, based on
    configuration and results from Analysis Hub. Currently, if transmitting, reads bits from a file and, if receiving,
    adds two to the received signal to create acknowledging signal.
    """

    def __init__(self, ahubq, sgenq, args):
        self.AHub = ahubq
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
        self.send_message()
        while not self.terminate:
            val = self.handle_messages()
            if val:
                self.send_message()

    def send_message(self):
        if self.transmitter:
            val = self.nextbit()
            signals = [2, 3]
            if self.lastrec != self.lastsent + 2 and self.lastrec is not None:
                print("TRANSMISSION ERROR")
        else:
            val = self.lastrec + 2
            signals = [0, 1]
        self.lastsent = val
        self.AHub.send([None, {"signals": signals}])
        self.SGen.put([None, {"type": "new data", "seed": val}])

    def handle_messages(self):
        message = self.AHub.recieve()
        if message[1]["type"] == "terminate":
            self.terminate = True
            self.SGen.put([None, {"type": "terminate"}])
            return False
        if message[1]["type"] == "new data":
            self.lastrec = message[1]["data"]
