import pyaudio


class PlayProc:

    def __init__(self, recq, sendq, args, config):
        self.samplerate = config["fs"]
        self.CHUNK = config["CHUNK"]
        self.recq = recq
        self.signalGen = sendq
        self.terminate = False
        self.incompleteChunk = b''
        self.lastsample = 0


    def callback(self, in_data, frame_count, time_info, status):
        data = self.incompleteChunk
        while len(data) < 2 * frame_count:
            if self.signalGen.empty():
                print("No data to play! Not keeping up! (or waiting for new signals)")
            data += self.signalGen.get()
        self.incompleteChunk = data[2 * frame_count:]
        data = data[:2 * frame_count]
        self.lastsample = data[-1]
        return data, pyaudio.paContinue

    def main(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                             rate=self.samplerate,
                             channels=1,
                             output=True,
                             stream_callback=self.callback)
        stream.start_stream()
        while not self.terminate:
            self.handle_messages()
        stream.stop_stream()
        stream.close()

    def handle_messages(self):
        message = self.recq.get()
        if message[1]["type"] == "terminate":
            self.terminate = True
            print("Terminating PlayProc!")
