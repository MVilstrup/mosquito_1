import asyncio
from urlparse import urlparse
from asyncio import PriorityQueue, Queue
from bloom.pybloomfilter import pybloomfilter


class Visited(object):
    """
    Coordinator used to keep track of all the URLs seen and what URLs to crawl
    next
    """

    def __init__(self, pull, recq, bloom_path='/tmp/seen_urls.bloom'):
        # Use a BloomFilter to figure out if the urls have been seen before
        self.seen_urls = pybloomfilter.BloomFilter(100000000, 0.01, bloom_path)

        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://localhost:{pull}".format(pull=pull))

        # Socket to send messages to
        self.server = context.socket(zmq.PUSH)
        self.server.connect("tcp://localhost:{push}".format(push=push))

    def add(self):
        """
        Add a list of URLs to the queue if they have not been seen before
        """
        while True:
            url = Url(instance=self.receiver.recv())
            self.seen_urls.add(url.to_string())

    def listen(self, url):
        """
        Checks wether this URL has been seen before
        """
        while True:
            url = Url(instance=self.server.recv())
            return url.to_string() in self.seen_urls
