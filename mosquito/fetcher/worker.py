import sys
import time
import zmq
import logging
import requests
from threading import Thread
from queue import Queue
from mosquito.messages import URL
from mosquito.messages.pages import HTMLPage


class Worker(object):

    def __init__(self, work_port, result_port, uid, loop=None, timeout=1):
        context = zmq.Context()

        self.logger = logging.getLogger('fetcher')
        hdlr = logging.FileHandler('fetcher.log')
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

        max_threads = 1
        self.work_queue = Queue(max_threads * 10)
        self.result_queue = Queue()

        threads = []
        for i in range(max_threads):
            thread = Thread(target=self._fetch)
            thread.start()
            threads.append(thread)

        while True:
            url = URL(instance=self.receiver.recv())
            self.work_queue.put(url)

            while not self.result_queue.empty():
                page = self.result_queue.get()
                self.sender.send(page.encode())

    def _fetch(self):
        while True:
            url = self.work_queue.get()
            try:
                url = url.to_string()
                print("Requesting : {}".format(url))
                r = requests.get(url, timeout=self.timeout)
                page = HTMLPage(response=r)
                self.result_queue.put(page)
            except Exception as exc:
                self.logger.info("ERROR: {} {}".format(url, exc))
