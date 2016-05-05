import sys
import time
import zmq
import logging
import requests
from threading import Thread
from queue import Queue

logger = logging.getLogger('fetcher')
hdlr = logging.FileHandler('fetcher.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Worker(object):

    def __init__(self, work_port, result_port, uid, loop=None, timeout=10):
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
            thread = Thread(target=self._fetch)
            thread.start()
            threads.append(thread)

        while True:
            url = self.receiver.recv_string()
            self.work_queue.put(url)

            while not self.result_queue.empty():
                page = self.result_queue.get()
                self.sender.send_json(page)

    def _fetch(self):
        while True:
            url = self.work_queue.get()
            try:
                print(url)
                r = requests.get(url, timeout=self.timeout)
                if r.status_code == 200:
                    self.result_queue.put((url, r.text))
            except Exception as exc:
                logger.info("ERROR: {} {}".format(url, exc))
