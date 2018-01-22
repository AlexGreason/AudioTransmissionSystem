import threading
import time


class Logger:
    """
    A basic sorta-threadsafe logger used for debugging purposes
    """

    def __init__(self, file):
        self.file = file
        self.lock = threading.Lock()
        self.starttime = time.time()

    def write_line(self, line):
        self.lock.acquire()
        try:
            self.file.write(str(time.time() - self.starttime) +": " + line + "\n")
        finally:
            self.lock.release()