from Queue import FifoQueue
import sys
import time
import zmq


class BackQueue(object):
    """
    BackQueue used to be polite towards domains by not crawling them
    to frequently
    """

    def __init__(self, push_port, request_port, queue_amount):
        super(BackQueue, self).__init__()
        assert queue_amount > 0

        self.queue_amount = queue_amount
        self.queues = []
        for i in range(queue_amount):
            self.queues.append(FifoQueue())

        context = zmq.Context()
        # Socket used to request a new batch of URLs from the FrontQueue
        self.request_urls = context.socket(zmq.REQ)
        self.request_urls.connect(request_port)

        # Socket used to request a new batch of URLs from the FrontQueue
        self.push_urls = context.socket(zmq.PUSH)
        self.push_urls.bind(push_port)

        while True:
            # Sleep in order to decrease the amount of URLs requested and sent out
            time.sleep(self.estimate_sleep_time())

            # Request URLs from the Coordinater
            self.request_urls.send_string("REQUEST")

            # Retrieve URLs from the Coordinater
            # Add the urls to the BackQueue afterwards
            urls = self.request_urls.recv_json()
            self.put_batch(urls)

            # Get a batch of URLs that have been through the BackQueue
            # Push these to the fetchers
            urls = self.get_batch()
            self.push_urls.send_json(urls)

    def put(self, url):
        parsed_uri = urlparse(url)
        location = parsed_uri.netloc
        queue_id = hash(location) % self.queue_amount
        self.queues[queue_id].put_nowait(url)

    def get_batch(self):
        urls = []
        for queue in self.queues:
            url = queue.get_nowait()
            if url is not None:
                urls.append(url)
        return urls

    def put_batch(self, urls):
        for url in urls:
            self.put(url)

    def qsize(self):
        size = 0
        for queue in self.queues:
            size += queue.qsize()
        return size

    def estimate_sleep_time(self):
        return 1
