import asyncio
import aiohttp  # Install with "pip install aiohttp".
from urlparse import urlparse
from asyncio import PriorityQueue, Queue
from bloom.pybloomfilter import pybloomfilter


class Coordinator(object):
    """
    Coordinator used to keep track of all the URLs seen and what URLs to crawl
    next
    """

    def __init__(self, roots):
        # Roots are a list of start URLs that should be crawled
        self.roots = roots

        self.loop = loop or asyncio.get_event_loop()

        # Use a priority queue in to figure out which URLs to visit next
        self.priority_queue = PriorityQueue(loop=self.loop)
        self.domain_visits = {}
        self.


        # Use a BloomFilter to figure out if the urls have been seen before
        self.seen_urls = pybloomfilter.BloomFilter(100000000, 0.01,
                                                   '/tmp/words.bloom')
        self.session = aiohttp.ClientSession(loop=self.loop)

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

    @asyncio.coroutine
    def get_urls(self, amount=None):
        """
        Method called in order to get a certain amount of URLs from the queue
        Returns an array of urls from the queue
        """
        if amount is None:
            amount = 1

        urls = []

        while len(urls) < amount:
            priority, url = yield from self.priority_queue.get()
            urls.append(url)

        return urls

    def get_domain(self, url):
        """
        Method used to extract a domain from a given URL
        """ 
        parsed_uri = urlparse(url)
        return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        
