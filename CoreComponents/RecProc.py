import pyaudio


class RecProc:
    """
    Records sounds and places the recordings into ahubq
    """

    def __init__(self, recq, ahubq, config):
        self.samplerate = config["fs"]
        self.CHUNK = config["CHUNK"]
        self.recq = recq
        self.aHub = ahubq
        self.terminate = False
        self.incompleteChunk = b''
        self.log = config["Logger"].write_line
        self.lastsample = 0
        self.numpackets = 0

    # noinspection PyUnusedLocal
    def callback(self, in_data, frame_count, time_info, status):
        self.incompleteChunk += in_data
        if len(self.incompleteChunk) >= 2 * self.CHUNK:
            self.numpackets += 1
            self.aHub.put(self.incompleteChunk[:2 * self.CHUNK])
            self.incompleteChunk = self.incompleteChunk[2 * self.CHUNK:]
            self.log("sending packet " + str(self.numpackets) + " to analysis hub")
        return in_data, pyaudio.paContinue

    def main(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        rate=self.samplerate,
                        channels=1,
                        input=True,
                        frames_per_buffer=self.CHUNK,
                        stream_callback=self.callback
                        )
        stream.start_stream()
        while not self.terminate:
            self.handle_messages()
        stream.stop_stream()
        stream.close()

    def handle_messages(self):
        message = self.recq.get()
        if message[1]["type"] == "terminate":
            self.terminate = True
            self.log("Terminating RecProc!")
