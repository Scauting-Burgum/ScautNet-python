from threading import Thread
from queue import Empty
from chat import Message

class ChatClientReceivingHandler(Thread):
  def __init__(self, client):
    super().__init__()
    self.client = client

  def run(self):
    while self.client.alive:
      try:
        message = self.client.pipeline.pull(timeout=1)
      except Empty:
        pass
      else:
        print("<{}> {}".format(message.sender, message.content))

class ChatClientSendingHandler(Thread):
  def __init__(self, client, sender):
    super().__init__()
    self.client = client
    self.sender = sender

  def run(self):
    while self.client.alive:
      try:
        content = input()
        message = Message(self.sender, content)
        self.client.pipeline.push(message)
      except KeyboardInterrupt:
        self.client.kill()
        return

from ScautNet import Client, Connection, TextFilter, Pipeline
from chat import MessageFilter

class ChatClient(Client):
  def get_pipeline(self):
    connection = Connection(self.socket)
    text_filter = TextFilter()
    message_filter = MessageFilter()
    return Pipeline(connection, text_filter, message_filter)

hostname = input("Hostname:")
port = int(input("Port:"))

nickname = input("Nickname:")

client = ChatClient(hostname, port)
client_receiving_handler = ChatClientReceivingHandler(client)
client_sending_handler = ChatClientSendingHandler(client, nickname)

client.start()

client_receiving_handler.start()
client_sending_handler.start()
