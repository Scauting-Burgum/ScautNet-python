from threading import Thread
from time import sleep

class Filter:
    def __init__(self):
        self._alive = True
    
    @property
    def alive(self):
        return self.receiving_thread.is_alive() and self.sending_thread.is_alive() and self._alive

    def kill(self):
        self._alive = False

    def start(self):
        self.receiving_thread.start()
        self.sending_thread.start()

class Pipeline(Thread):
    def __init__(self, *filters):
        super().__init__()
        self.filters = filters
        for i in range(len(filters)):
            _filter = filters[i]
            _filter.pipeline = self
            _filter.index = i
            _filter.start()
        self.start()

    def push(self, data):
        self.filters[-1].sending_thread.queue.put(data)

    def pull(self, timeout=1):
        return self.filters[-1].receiving_thread.queue.get(timeout = timeout)

    def run(self):
        while True:
            for _filter in self.filters:
                if not _filter.alive:
                    for _filter in self.filters:
                        _filter.kill()
                    return

