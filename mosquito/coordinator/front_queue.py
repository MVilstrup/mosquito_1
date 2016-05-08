from queue import PriorityQueue
from pybloomfilter import BloomFilter
import zmq
import logging
from mosquito.messages import DataList, URL


class FrontQueue(object):
    """
    FrontQueue used to be polite towards domains by not crawling them
    to frequently
    """

    def __init__(self, pull_port, respond_port, roots):
        super(FrontQueue, self).__init__()
        context = zmq.Context()

        self.logger = logging.getLogger('front_queue')
        hdlr = logging.FileHandler('front_queue.log')
        formatter = logging.Formatter(
            '%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        self.queue = PriorityQueue()

        # Use a BloomFilter to figure out if the urls have been seen before
        self.seen_urls = BloomFilter(100000000, 0.01, b'urls.bloom')

        # Add all roots to the seen_urls and PriorityQueue
        self.add_urls([URL(url=url) for url in roots])

        # Socket to receive found URLs on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(pull_port)

        # Socket to recieve requsts from the coordinator for new URLs
        self.responder = context.socket(zmq.REP)
        self.responder.bind(respond_port)

        # Poller used to switch between the two sockets
        poller = zmq.Poller()
        poller.register(self.receiver, zmq.POLLIN)
        poller.register(self.responder, zmq.POLLIN)

        while True:
            sockets = dict(poller.poll())
            try:
                if self.receiver in sockets and sockets[
                        self.receiver] == zmq.POLLIN:
                    url_lists = DataList(instance=self.receiver.recv())
                    for url_list in url_lists:
                        self.add_urls(url_list)

                if self.responder in sockets and sockets[
                        self.responder] == zmq.POLLIN:
                    request = self.responder.recv_string()

                    # Check the request is proper
                    if not request or request != "REQUEST":
                        continue

                    urls = self.get_batch()
                    url_list = DataList(type="URLS", elements=urls)
                    self.responder.send(url_list.encode())
            except Exception as exc:
                self.logger.error("ERROR: {}".format(exc))

    def add_urls(self, urls):
        """
        Add a list of URLs to the queue if they have not been seen before
        """
        new_urls = [url for url in urls if not self._is_seen(url)]
        self.update_seen(new_urls)

        for url in urls:
            self.queue.put(url)

        self.logger.info("{} of {} found urls was new".format(
            len(new_urls), len(urls)))

    def _is_seen(self, url):
        """
        Checks wether this URL has been seen before
        """
        return url.to_bytes() in self.seen_urls

    def update_seen(self, urls):
        self.seen_urls.update([url.to_bytes() for url in urls])

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
