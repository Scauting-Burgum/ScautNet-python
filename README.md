# ScautNet-python
A networking library for python.

## Installation
First, download the newest version of ScautNet from the [releases page].  
Inside the zip-file you'll find a folder, put this folder inside your project's folder.

[releases page]: https://github.com/Scauting-Burgum/ScautNet-python/releases

## Example
In this example, you'll create a chat application.

To get started, make a folder where you'll be saving all your code.  
Create a folder inside of this folder, call this folder "ScautNet".  
Then take the contents of this project and put them in that folder.
### Creating the common code
Let's make a file called "chat.py".

The first thing in this file will be a class for chat messages;
```python
class Message:
  def __init__(self, sender, content):
    self.sender = sender
    self.content = content
```

Next, add methods for converting messages to JSON and JSON back to messages;
```python
import json

def message_from_json(json_):
  return Message(**json.loads(json_))

def message_to_json(message):
  return json.dumps({'sender':message.sender, 'content':message.content})
```

Now we'll create a class to receive messages;
```python
from threading import Thread
from queue import Queue, Empty

class MessageFilterReceivingThread(Thread):
  def __init__(self, message_filter):
    super().__init__()
    self.message_filter = message_filter
    self.queue = Queue()

  def run(self):
    previous_filter = self.message_filter.pipeline.filters[self.message_filter.index - 1]
    while True:
      json = None
      while json is None:
        try:
          json = previous_filter.pull(timeout = 1)
        except Empty:
          if not self.message_filter.alive:
            return

      message = message_from_json(json)
      self.queue.put(message)
```

We'll also need a class to send messages;
```python
class MessageFilterSendingThread(Thread):
  def __init__(self, message_filter):
    super().__init__()
    self.message_filter = message_filter
    self.queue = Queue()

  def run(self):
    previous_filter = self.message_filter.pipeline.filters[self.message_filter.index - 1]
    while True:
      message = None
      while message is None:
        try:
          message = self.queue.get(timeout = 1)
        except Empty:
          if not self.message_filter.alive:
            return

      json = message_to_json(message)
      previous_filter.push(json)
```

Now we can combine these classes into a filter;
```python
from ScautNet import Filter

class MessageFilter(Filter):
  def __init__(self):
    super().__init__()
    self.receiving_thread = MessageFilterReceivingThread(self)
    self.sending_thread = MessageFilterSendingThread(self)
```

### Server
Now it's time to create a server, to do this, first create a file called "server.py".

We'll start by making a class which forwards any message to all clients;
```python
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
```

Now we'll have to create a server class;
```python
from ScautNet import Server, Connection, TextFilter, Pipeline
from chat import MessageFilter

class ChatServer(Server):
  def get_pipeline(self, socket):
    connection = Connection(socket)
    text_filter = TextFilter()
    message_filter = MessageFilter()
    return Pipeline(connection, text_filter, message_filter)
```

Now we just have to start the server!
```python
hostname = "localhost"
port = 5000

server = ChatServer(hostname, port)
server_handler = ChatServerHandler(server)

server.start()

server_handler.start()
```
### Client
For the client we'll make another file, call this file "client.py".

Again, we'll create classes to handle our logic, but in this case we'll need to make two separate classes;
```python
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
```

Now we'll need a client class;
```python
from ScautNet import Client, Connection, TextFilter, Pipeline
from chat import MessageFilter

class ChatClient(Client):
  def get_pipeline(self):
    connection = Connection(self.socket)
    text_filter = TextFilter()
    message_filter = MessageFilter()
    return Pipeline(connection, text_filter, message_filter)
```

After this we can start the client;
```python
hostname = input("Hostname:")
port = int(input("Port:"))

nickname = input("Nickname:")

client = ChatClient(hostname, port)
client_receiving_handler = ChatClientReceivingHandler(client)
client_sending_handler = ChatClientSendingHandler(client, nickname)

client.start()

client_receiving_handler.start()
client_sending_handler.start()
```

That's it, now just start the server, start some clients, and voila; you've made a chat application!
