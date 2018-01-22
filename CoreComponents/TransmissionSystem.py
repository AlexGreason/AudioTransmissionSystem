from CallBack import CallBack

class TSystem:
    def __init__(self):
        # note: not actual processes
        # wrapper classes which also expose queues in both directions to allow communications

        self.signalGen = None
        # given data to transmit from dataSource, generates samples in realtime and
        # sends them to playProc to be played (has a queue to handle lagspikes)
        # two (or more) instances of signalGen: one getting samples to play, one (or more)
        # generating templates to search for for analysis threads

        self.analysisHub = None
        # has a set of child processes, one for each signal being searched for
        # what to search for comes from dataSource, templates from signalGen
        # analysisHub collates search results and decides when to accept a signal as having been received

        self.playProc = None
        # has an instance of signalGen generating samples
        # has a queue of samples to be played to maintain realtime nature

        self.receiveProc = None
        # no processing, sends data directly to analysisHub, where it gets stored in a queue to be analyzed

        self.dataSource = None
        # given what was last received, decides both what to send next and what to search for next

        self.transmitter = True
        # True if this is the transmitter, false if it the receiver, may take other values if I implement
        # bidirectional communication

        self.callback = CallBack(0, "main thread")
        # wrapper class, "leaves a name and number" : unique process ID, what type of process this is

    def main(self):
        """
        1. wait until time to send (immediately if transmitter, after first bit if receiver)
        2. get seed from dataSource (next bit if transmitter, acknowledgement if receiver)
        3. send seed to signalGen, signalGen starts stacking up chunks of new signal for playProc
            clears play queue if nonempty before doing so
        4. analysisHub discards old data, recieves new search queries (also from dataSource)
        5. receiveProc doesn't change anything, keeps sending data to analysisHub
            playProc might halt for a bit until signalGen catches up, that's fine
        """

        last_data = self.transmitter

        while self.dataSource.getResponse(self.callback, "has data"):  # checks if transmission is complete

            self.handle_messages()
            # goes through messages in self.callback and does whatever is needed

    def handle_messages(self):
        pass

    def handle_data(self, data):
        pass
