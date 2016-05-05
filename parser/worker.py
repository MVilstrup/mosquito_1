import sys
import time
import zmq
import logging
import requests
from threading import Thread
from queue import Queue
from lxml.html import document_fromstring

logger = logging.getLogger('parser')
hdlr = logging.FileHandler('parser.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Worker(object):

    def __init__(self, work_port, result_port, uid, timeout=10):
        context = zmq.Context()
        self.id = uid
        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(work_port)

        # Socket to send messages to
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect(result_port)
        self.timeout = timeout

        max_threads = 10
        self.work_queue = Queue(max_threads * 10)
        self.result_queue = Queue()

        threads = []
        for i in range(max_threads):
            thread = Thread(target=self._extract_links)
            thread.start()
            threads.append(thread)

        logger.info("Started workers, waiting for pages")
        while True:
            page = self.receiver.recv_json()
            self.work_queue.put(page)

            while not self.result_queue.empty():
                page, found_links = self.result_queue.get()
                logger.info("Parsed page")
                self.sender.send_json([page, found_links])

    def _extract_links(self):
        while True:
            url, page = self.work_queue.get()
            """ Extract hrefs """
            try:
                dom = document_fromstring(page)
                dom.make_links_absolute(url)
                links = dom.cssselect('a')
                self.result_queue.put((url, [link.get(
                    'href') for link in links if link.get('href')]))
            except:
                continue
