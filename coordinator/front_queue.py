from queue import PriorityQueue
from .bloom.pybloomfilter import pybloomfilter
import zmq

class FrontQueue(object):
    """
    FrontQueue used to be polite towards domains by not crawling them
    to frequently
    """
    def __init__(self pull_port, respond_port, roots):
        super(FrontQueue, self).__init__()
        context = zmq.Context()

        self.queue = PriorityQueue()

        # Use a BloomFilter to figure out if the urls have been seen before
        self.seen_urls = pybloomfilter.BloomFilter(100000000, 0.01,
                                                   'urls.bloom')

        # Add all roots to the seen_urls and PriorityQueue
        self.add_urls(roots)

        # Socket to receive found URLs on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(pull_port)

        # Socket to recieve requsts from the coordinator for new URLs
        self.responder = context.socket(zmq.REP)
        self.responder.connect(respond_port)

        # Poller used to switch between the two sockets
        poller = zmq.Poller()
        poller.register(receiver, zmq.POLLIN)
        poller.register(responder, zmq.POLLIN)

        while True:
            sockets = dict(poller.poll())

            if receiver in sockets and sockets[receiver] == zmq.POLLIN:
                urls = self.receiver.recv_json()
                self.add_urls(urls)

            if responder in sockets and sockets[responder] == zmq.POLLIN:
                request = self.responder.recv_string()

                # Check the request is proper
                if not request or request != "REQUEST":
                    continue

                urls = self.get_batch()
                self.responder.send_json(urls)



    def add_urls(self, urls):
        """
        Add a list of URLs to the queue if they have not been seen before
        """
        new_urls = []
        for priority, url in urls:
            if not self._is_seen(url):
                self.queue.put((priority, url))
                new_urls.append(url)

        self.seen_urls.update(new_urls)

    def _is_seen(self, url):
        """
        Checks wether this URL has been seen before
        """
        return url in self.seen_urls

    def get_batch(self):
        """
        Retrieve a batch of urls to crawl. The maximum amount of urls retreived
        is 1000, but if the queue does not contain that many all urls in the
        PriorityQueue is returned
        """
        urls = []
        for i in range(1000):
            if self.queue.empty():
                break

            urls.append(self.queue.get())

        return urls
