import sys
import time
import zmq
import logging
import requests
from threading import Thread
from queue import Queue

from mosquito.messages.pages import HTMLPage
from mosquito.messages import DataList


class Worker(object):

    def __init__(self, work_port, result_port, uid, timeout=10):
        context = zmq.Context()

        self.logger = logging.getLogger('parser')
        hdlr = logging.FileHandler('parser.log')
        formatter = logging.Formatter(
            '%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

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
            thread = Thread(target=self.prioritize_links)
            thread.start()
            threads.append(thread)

        self.logger.info("Started workers, waiting for pages")
        while True:
            try:
                page = HTMLPage(instance=self.receiver.recv())
                self.work_queue.put(page)

                while not self.result_queue.empty():
                    found_links = self.result_queue.get()
                    link_list = DataList(type="URLS", elements=found_links)
                    self.sender.send(link_list.encode())
            except Exception as exc:
                self.logger.warning("ERROR: {}".format(exc))

    def prioritize_links(self):
        while True:
            page = self.work_queue.get()
            """ Extract hrefs """
            links = page.get_links()
            for link in links:
                link.priority = 1

            self.result_queue.put(links)
