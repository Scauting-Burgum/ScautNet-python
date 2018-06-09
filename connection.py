from . import pipeline
from threading import Thread
from socket import timeout
from queue import Queue, Empty

class ConnectionReceivingThread(Thread):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.queue = Queue()

    def run(self):
        while True:
            try:
                self.queue.put(
                    self.connection.socket.recv(1)
                    )
            except timeout:
                if not self.connection.alive:
                    return
            except (ConnectionResetError, ConnectionAbortedError):
                return

class ConnectionSendingThread(Thread):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.queue = Queue()

    def run(self):
        while True:
            try:
                self.connection.socket.send(
                    self.queue.get(timeout=1)
                    )
            except Empty:
                if not self.connection.alive:
                    return
            except (ConnectionResetError, ConnectionAbortedError):
                return

class Connection(pipeline.Filter):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.sending_thread = ConnectionSendingThread(self)
        self.receiving_thread = ConnectionReceivingThread(self)

    def kill(self):
        self.socket.close()
        super().kill()
