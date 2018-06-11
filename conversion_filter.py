from queue import Queue, Empty

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
