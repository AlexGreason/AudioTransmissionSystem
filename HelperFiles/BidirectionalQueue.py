import multiprocessing as mp

"""
Bidirectional Queue
This is used instead of a Pipe because it allows easier implementation of 
maximum sizes and blocking/nonblocking/limited-time blocking reads and writes
"""
class BQueue:

    def __init__(self, maxsize=0):
        self.queuesend = mp.Queue(maxsize=maxsize)
        self.queuerec = mp.Queue(maxsize=maxsize)

    def invert(self):
        temp = self.queuesend
        self.queuesend = self.queuerec
        self.queuerec = temp

    def send(self, value, timeout=None):
        self.queuesend.put(value, timeout=timeout)

    def recieve(self, timeout=None):
        return self.queuerec.get(timeout=timeout)

    def size(self):
        return self.queuerec.qsize()

    def empty(self):
        return self.queuerec.empty()
