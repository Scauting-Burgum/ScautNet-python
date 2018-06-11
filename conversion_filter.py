from threading import Thread
from queue import Queue, Empty
from . import pipeline

class ConversionFilterReceivingThread(Thread):
    def __init__(self, conversion_filter):
        super().__init__()
        self.conversion_filter = conversion_filter
        self.queue = Queue()

    def run(self):
        previous_filter = self.conversion_filter.pipeline.filters[self.conversion_filter.index - 1]
        while True:
            message = None
            while message is None:
                try:
                    message = previous_filter.pull()
                except Empty:
                    if not self.conversion_filter.alive:
                        return
            converted_message = self.conversion_filter.receiving_converter(message)
            self.queue.put(converted_message)

class ConversionFilterSendingThread(Thread):
    def __init__(self, conversion_filter):
        super().__init__()
        self.conversion_filter = conversion_filter
        self.queue = Queue()

    def run(self):
        previous_filter = self.conversion_filter.pipeline.filters[self.conversion_filter.index - 1]
        while True:
            message = None
            while message is None:
                try:
                    message = self.queue.get(timeout = 1)
                except Empty:
                    if not self.conversion_filter.alive:
                        return
            converted_message = self.conversion_filter.sending_converter(message)
            previous_filter.push(converted_message)

class ConversionFilter(pipeline.Filter):
    def __init__(self, receiving_converter, sending_converter):
        super().__init__()
        self.receiving_converter = receiving_converter
        self.sending_converter = sending_converter
        
        self.receiving_thread = ConversionFilterReceivingThread(self)
        self.sending_thread = ConversionFilterSendingThread(self)
