from threading import Thread, Lock
from socket import socket, timeout
from . import connection as connection_module
from . import pipeline as pipeline_module

class Server(Thread):
    def __init__(self, hostname, port):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.pipelines_lock = Lock()
        self.pipelines = set()
        self._alive = True

    def get_pipeline(self, socket):
        connection = connection_module.Connection(socket)
        return pipeline_module.Pipeline(connection)

    def start(self):
        self.socket = socket()
        self.socket.settimeout(1)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(5)
        super().start()

    def run(self):
        try:
            while True:
                try:
                    client_socket, client_address = self.socket.accept()
                    pipeline = self.get_pipeline(client_socket)
                    with self.pipelines_lock:
                        self.pipelines.add(pipeline)
                except timeout:
                    if not self.alive:
                        return
        finally:
            self.socket.close()
            with self.pipelines_lock:
                for pipeline in self.pipelines:
                    pipeline.kill()

    @property
    def alive(self):
        return self.is_alive() and self._alive

    def kill(self):
        self._alive = False
