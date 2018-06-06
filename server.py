from threading import Thread, Lock
from socket import socket, timeout
from connection import Connection
from pipeline import Pipeline

class Server(Thread):
    def __init__(self, hostname, port):
        super().__init__()
        self.hostname = hostname
        self.port = port
        self.pipelines_lock = Lock()
        self.pipelines = set()
        self.alive = False

    def get_pipeline(self, socket):
        connection = Connection(socket)
        return Pipeline(connection)

    def run(self):
        self.socket = socket()
        self.socket.settimeout(1)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(5)

        try:
            self.alive = True
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
            self.alive = False

    def kill(self):
        self.alive = False
