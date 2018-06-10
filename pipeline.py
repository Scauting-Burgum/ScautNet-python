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

    def pull(self, timeout = 1):
        return self.receiving_thread.queue.get(timeout=1)

    def push(self, data):
        self.sending_thread.queue.put(data)

class Pipeline(Thread):
    def __init__(self, *filters):
        super().__init__()
        self._alive = True
        self.filters = filters
        for i in range(len(filters)):
            _filter = filters[i]
            _filter.pipeline = self
            _filter.index = i
            _filter.start()
        self.start()

    def push(self, data):
        self.filters[-1].push(data)

    def pull(self, timeout=1):
        return self.filters[-1].pull(timeout = timeout)

    def run(self):
        while True:
            for _filter in self.filters:
                if not (_filter.alive and self.alive):
                    for _filter in self.filters:
                        _filter.kill()
                    return

    @property
    def alive(self):
        return self.is_alive() and self._alive

    def kill(self):
        self._alive = False
