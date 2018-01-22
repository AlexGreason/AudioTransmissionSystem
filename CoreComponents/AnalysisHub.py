class AHub:
    """
    Analysis Hub. Creates analysis child processes to search for the signals specified by Data Generator, takes
    in data from the recording process and distributes it to each child, determines if a signal has been received
    and if so which one, and then sends that information to Data Generator. Intermittently sends results of analysis
    so far to Data Sink for display and logging.
    """

    def __init__(self, recq, recprocq, datagenq, sinkq, args, config):
        self.data = None
        self.recq = recq
        self.recProc = recprocq
        self.dataGen = datagenq
        self.dataSink = sinkq
        self.sigthreshold = config["Minimum Significance"]
        self.sigfactor = config["Significance Factor"]
        childpackage, childclass, achild = config["aChild"]
        self.aChild = vars(vars(__import__(childpackage, globals(), locals(), [achild], 0))[childclass])[achild].__func__
        # aChild is a function that takes a signal identifier
        # and creates and starts a process with an analysis child
        # searching for that signal, and returns a sendq and recq for that child
        self.aChildren = []
        self.aResults = []
        self.terminate = False
        self.conclusive = False
        self.config = config
        self.args = args
        self.log = config["Logger"].write_line
        self.id = 0

    def main(self):
        while not self.terminate:
            # get new data
            while self.dataGen.empty() and not self.terminate:
                self.handle_messages()
            self.data = self.dataGen.get()
            # destroy old children, create new ones (repurpose?)
            for send, rec in self.aChildren:
                send.put([None, {"type": "terminate"}])
            self.aChildren = [self.aChild(x, self.args, self.config) for x in self.data[1]["signals"]]
            self.aResults = [[x, None, False] for x in range(len(self.aChildren))]
            # not-conclusive-yet loop
            self.conclusive = False
            while self.dataGen.empty() and not self.terminate and not self.conclusive:
                # get new recorded signal, update children
                while not self.recProc.empty():
                    signal = self.recProc.get()
                    self.id += 1
                    self.log("recieved packet number: " + str(self.id) + ", sending to children")
                    for send, rec in self.aChildren:
                        send.put([None, {"type": "new data", "data": signal, "id": self.id}])
                # get current analysis results (if more than one in queue, overwrites old, fix to allow plotting)
                newresults = False
                for i, (send, rec) in enumerate(self.aChildren):
                    if not rec.empty():
                        newresults = True
                        self.aResults[i][1] = rec.get()
                        self.aResults[i][2] = True
                # send current results
                if newresults:
                    self.sendData()
                self.handle_messages()
                # check if current analysis results are conclusive
                self.conclusive = self.isConclusive()

    def isConclusive(self):
        for val in self.aResults:
            if val[1] is None:
                return False
        sigs = sorted(self.aResults, key=lambda x: x[1][1]["significance"], reverse=True)
        if sigs[0][1][1]["significance"] >= self.sigthreshold and \
                        sigs[0][1][1]["significance"] >= sigs[1][1][1]["significance"] * self.sigfactor:
            val = sigs[0][1][1]["signalnum"]
            self.dataGen.put([None, {"type": "new data", "data": val}])
            self.dataSink.put([None, {"type": "recieved signal", "data": val}])
            return True
        return False

    def sendData(self):
        for x in self.aResults:
            i, data, updated = x
            if data is not None and updated:
                self.dataSink.put([None, {"type":"new data", "data":data[1]}])
                x[2] = False

    def handle_messages(self):
        if not self.recq.empty():
            message = self.recq.get()
            if message[1]["type"] == "terminate":
                self.terminate = True
                self.log("Terminating Analysis Hub!")
