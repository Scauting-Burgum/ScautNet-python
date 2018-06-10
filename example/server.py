from threading import Thread
from queue import Empty

class ChatServerHandler(Thread):
  def __init__(self, server):
    super().__init__()
    self.server = server

  def run(self):
    while self.server.alive:
      with self.server.pipelines_lock:
        for pipeline in self.server.pipelines:
          try:
            message = pipeline.pull(timeout=0.2)
          except Empty:
            pass
          else:
            for pipeline_ in self.server.pipelines:
              pipeline_.push(message)

from ScautNet import Server, Connection, TextFilter, Pipeline
from chat import MessageFilter

class ChatServer(Server):
  def get_pipeline(self, socket):
    connection = Connection(socket)
    text_filter = TextFilter()
    message_filter = MessageFilter()
    return Pipeline(connection, text_filter, message_filter)

hostname = "localhost"
port = 5000

server = ChatServer(hostname, port)
server_handler = ChatServerHandler(server)

server.start()

server_handler.start()
