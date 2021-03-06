from . import connection as connection_module
from . import pipeline as pipeline_module
from threading import Thread
from socket import socket

class Client(Thread):
    def __init__(self, hostname, port):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self._alive = True

    def get_pipeline(self):
        connection = connection_module.Connection(self.socket)
        pipeline = pipeline_module.Pipeline(connection)
        return pipeline

    def start(self):
        self.socket = socket()
        self.socket.settimeout(1)
        self.socket.connect((self.hostname, self.port))
        self.pipeline = self.get_pipeline()
        super().start()

    def run(self):
        try:
            while self.alive and self.pipeline.alive:
                pass
        finally:
            self.pipeline.kill()

    def push(self, data):
        self.pipeline.push(data)

    def pull(self, timeout = 1):
        return self.pipeline.pull(timeout = timeout)

    @property
    def alive(self):
        return self.is_alive() and self._alive

    def kill(self):
        self._alive = False
