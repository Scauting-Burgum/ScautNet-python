class Message:
  def __init__(self, sender, content):
    self.sender = sender
    self.content = content

import json

def message_from_json(json_):
  return Message(**json.loads(json_))

def message_to_json(message):
  return json.dumps({'sender':message.sender, 'content':message.content})

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
          json = previous_filter.receiving_thread.queue.get(timeout = 1)
        except Empty:
          if not self.message_filter.alive:
            return

      message = message_from_json(json)
      self.queue.put(message)

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
      previous_filter.sending_thread.queue.put(json)

from ScautNet import Filter

class MessageFilter(Filter):
  def __init__(self):
    super().__init__()
    self.receiving_thread = MessageFilterReceivingThread(self)
    self.sending_thread = MessageFilterSendingThread(self)
