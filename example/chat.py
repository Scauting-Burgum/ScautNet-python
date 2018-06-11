class Message:
  def __init__(self, sender, content):
    self.sender = sender
    self.content = content

import json

def message_from_json(json_):
  return Message(**json.loads(json_))

def message_to_json(message):
  return json.dumps({'sender':message.sender, 'content':message.content})

from ScautNet import ConversionFilter

class MessageFilter(ConversionFilter):
  def __init__(self):
    super().__init__(message_from_json, message_to_json)

