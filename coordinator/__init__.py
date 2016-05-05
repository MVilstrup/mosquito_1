from urlparse import urlparse
from bloom.pybloomfilter import pybloomfilter
from Queue import PriorityQueue
import zmq


class Coordinator(object):
    """
    Coordinator used to keep track of all the URLs seen and what URLs to crawl
    next
    """

    def __init__(self, roots, inbound_port, outbound_port):
        # Roots are a list of start URLs that should be crawled
        self.roots = roots

        # Use a BloomFilter to figure out if the urls have been seen before
        self.seen_urls = pybloomfilter.BloomFilter(100000000, 0.01,
                                                   '/tmp/words.bloom')

        # Add the roots to the seen urls
        self.add_urls(roots)

        # Use a priority queue in to figure out which URLs to visit next
        self.front_queue = PriorityQueue()
        self.domain_visits = {}

        context = zmq.Context()
        # Socket to receive lists of urls that should be sent
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(inbound_port)

        # Socket to send messages onto the workers to resolve the domain
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind(outbound_port)

    def listen(self):
        pass

    def push(self):
        pass

    def maintain(self):
        pass

    def add_urls(self, urls):
        """
        Add a list of URLs to the queue if they have not been seen before
        """
        new_urls = []
        for priority, url in urls:
            if not self._is_seen(url):
                self.priority_queue.put_nowait((priority, url))
                new_urls.append(url)

        self.seen_urls.update(new_urls)

    def _is_seen(self, url):
        """
        Checks wether this URL has been seen before
        """
        return url in self.seen_urls

    def get_domain(self, url):
        """
        Method used to extract a domain from a given URL
        """
        parsed_uri = urlparse(url)
        return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
