from queue import Queue
import sys
import time
import zmq
import logging
from urllib.parse import urlparse
from mosquito.messages import DataList, Message, URL


class BackQueue(object):
    """
    BackQueue used to be polite towards domains by not crawling them
    to frequently
    """

    def __init__(self, push_port, request_port, queue_amount):
        super(BackQueue, self).__init__()
        self.logger = logging.getLogger('back_queue')
        hdlr = logging.FileHandler('back_queue.log')
        formatter = logging.Formatter(
            '%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        assert queue_amount > 0

        self.queue_amount = queue_amount
        self.queues = []
        for i in range(queue_amount):
            self.queues.append(Queue())

        context = zmq.Context()
        # Socket used to request a new batch of URLs from the FrontQueue
        self.request_urls = context.socket(zmq.REQ)
        self.request_urls.connect(request_port)
        self.logger.info("Connected to Coordinator on {}".format(request_port))

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
            urls = DataList(instance=self.request_urls.recv())
            self.put_batch(urls)

            # Get a batch of URLs that have been through the BackQueue
            # Push these to the fetchers

            batch = self.get_batch()
            if batch:
                urls = DataList(type="URLS", elements=batch)
                self.logger.info("Pushing {} urls".format(len(urls)))
                self.push_urls.send(urls.encode())

    def put(self, url):
        queue_id = hash(url.location) % self.queue_amount
        self.queues[queue_id].put_nowait(url)

    def get_batch(self):
        urls = []
        for queue in self.queues:
            if queue.empty():
                continue

            urls.append(queue.get_nowait())

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
