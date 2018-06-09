from . import connection
from . import pipeline
from threading import Thread
from socket import socket

class Client(Thread):
    def __init__(self, hostname, port):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.alive = False

    def get_pipeline(self):
        connection = connection.Connection(self.socket)
        pipeline = pipeline.Pipeline(connection)
        return pipeline

    @property
    def sending_queue(self):
        return self.pipeline.filters[-1].sending_thread.queue

    @property
    def receiving_queue(self):
        return self.pipeline.filters[-1].receiving_thread.queue

    def run(self):
        self.socket = socket()
        self.socket.settimeout(1)
        self.socket.connect((self.hostname, self.port))
        self.pipeline = self.get_pipeline()
        self.alive = True

        try:
            while self.alive and self.pipeline.alive:
                pass
        finally:
            self.pipeline.kill()
            self.alive = False
