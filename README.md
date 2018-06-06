# ScautNet-python
A networking library for python.

## Installation
First, download the newest version of ScautNet from the [releases page].  
Inside the zip-file you'll find a folder, put this folder inside your project's folder.

[releases page]: https://github.com/Scauting-Burgum/ScautNet-python/releases

## Example ***(OUTDATED)***
In this example you'll be making a simple application that logs whatever is sent to the server.

First make a new folder, then install ScautNet in there.  
Then create a file, let's call this one `log_client.py`.

The first thing you'll have to do when using ScautNet is to import the parts you need;
```python
from ScautNet import Connection, TextFilter, Pipeline
```

You'll also need to import `socket`;
```python
from socket import socket
```

Now we can start making an application,  
first you'll want to prompt the user for the server's hostname and port;
```python
hostname = input("Server hostname:")
port = int(input("Server port:"))
```

Now you can create a socket, set a timeout, and connect to the server;
```python
my_socket = socket()
my_socket.settimeout(1)
my_socket.connect((hostname, port))
```
**Always set a timeout on your sockets when using ScautNet, error handling doesn't function properly if you don't.**

Alright, now you can start using ScautNet;
```python
connection = Connection(my_socket)
text_filter = TextFilter()
pipeline = Pipeline(connection, text_filter)
pipeline.start()
```

Now you'll just have to take some user input and send it to the server;
```python
try:
  while True:
    message = input("Message:")
    pipeline.push(message)
finally:
  my_socket.close()
```

Okay, you've created a client, now make another file, call this one `log_server.py`.  
The first lines will actually be exactly the same, although we do need two more imports;
```python
from ScautNet import Connection, TextFilter, Pipeline

from socket import socket

from threading import Thread

from queue import Empty
```

Now, you can set up a server socket;
```python
server_socket = socket()

port = int(input("Port:"))
server_socket.bind(("localhost", port))

server_socket.listen(5)
```

Now you'll need to make a while loop that will keep receiving connections, and make pipelines for each client and then print out all messages that get received;
```python
try:
  while True:
    client_socket, client_address = server_socket.accept()

    connection = Connection(client_socket)
    text_filter = TextFilter()
    pipeline = Pipeline(connection, text_filter)
    pipeline.start()

    def log():
      while True:
        try:
          print(pipeline.pull(timeout=1))
        except Empty:
          if not pipeline.filters[-1].alive:
            return

    Thread(target=log).start()
finally:
  server_socket.close()
```
