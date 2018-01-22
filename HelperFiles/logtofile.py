import threading
import time
import logging
import random

class Logger:

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