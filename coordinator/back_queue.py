from Queue import FifoQueue
import sys
import time


class BackQueue(object):
    """
    BackQueue used to be polite towards domains by not crawling them
    to frequently
    """

    def __init__(self, queue_amount=10):
        super(BackQueue, self).__init__()
        assert queue_amount > 0

        self.queue_amount = queue_amount
        self.queues = []
        self.current_queue = 0
        for i in range(queue_amount):
            self.queues.append(FifoQueue())

    def put(self, url):
        parsed_uri = urlparse(url)
        location = parsed_uri.netloc
        queue_id = hash(location) % self.queue_amount
        self.queues[queue_id].put_nowait(url)

    def get(self):
        found = False
        while not found:
            url = self.queues[self.current_queue].get_nowait()
            self.current_queue = (self.current_queue + 1) % self.queue_amount
            if url is not None:
                return url
