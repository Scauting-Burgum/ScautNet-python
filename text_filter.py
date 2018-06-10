from . import pipeline
from threading import Thread
from queue import Queue, Empty

class TextFilterReceivingThread(Thread):
    def __init__(self, text_filter):
        super().__init__()
        self.text_filter = text_filter
        self.queue = Queue()

    def run(self):
        previous_filter = self.text_filter.pipeline.filters[self.text_filter.index - 1]
        while True:
            length_bytes = []
            while len(length_bytes) < 4:
                try:
                    length_bytes.append(previous_filter
                                        .pull(
                                            timeout=1)
                                        )
                except Empty:
                    if not self.text_filter.alive:
                        return
            length = int.from_bytes(b''.join(length_bytes), "little")

            content_bytes = []
            while len(content_bytes) < length:
                try:
                    content_bytes.append(previous_filter
                                         .receiving_thread.queue.get(
                                             timeout=1)
                                         )
                except Empty:
                    if not self.text_filter.alive:
                        return
            self.queue.put(b''.join(content_bytes).decode("utf-8"))

class TextFilterSendingThread(Thread):
    def __init__(self, text_filter):
        super().__init__()
        self.text_filter = text_filter
        self.queue = Queue()

    def run(self):
        previous_filter = self.text_filter.pipeline.filters[self.text_filter.index - 1]
        while True:
            content = None
            while content is None:
                try:
                    content = self.queue.get(timeout=1)
                except Empty:
                    if not self.text_filter.alive:
                        return

            content_bytes = content.encode("utf-8")
            length = len(content_bytes)
            length_bytes = length.to_bytes(4, "little")

            previous_filter.push(
                b''.join([length_bytes, content_bytes]))

class TextFilter(pipeline.Filter):
    def __init__(self):
        super().__init__()
        self.sending_thread = TextFilterSendingThread(self)
        self.receiving_thread = TextFilterReceivingThread(self)
