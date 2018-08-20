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
            self.file.write(str(time.time() - self.starttime) +" | " + line + "\n")
        finally:
            self.lock.release()

def sortlog(file):
    entries = []
    with open(file, "r") as f:
        for line in f:
            time, entry = line.split("|")
            entries.append((float(time), entry))
    entries.sort(key=lambda x: x[0])
    with open(file, "w") as f:
        for entry in entries:
            f.write(str(entry[0]) + " | " + entry[1])

if __name__ == "__main__":
    sortlog("../TestingCode/logfile.txt")
