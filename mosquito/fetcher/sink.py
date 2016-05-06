# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket

import zmq
import logging



class Sink(object):

    def __init__(self, result_port, send_port):
        context = zmq.Context()


        self.logger = logging.getLogger('fetcher')
        hdlr = logging.FileHandler('fetcher.log')
        formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        # Socket to receive messages on
        self.result_port = context.socket(zmq.PULL)
        self.result_port.bind(result_port)

        # Socket to reschedule domains that timed out
        self.send_port = context.socket(zmq.PUSH)
        self.send_port.bind(send_port)
        self._forward()

    def _forward(self):
        pages = []
        while True:
            url, page = self.result_port.recv_json()
            pages.append((url, page))

            if len(pages) >= 10:
                self.logger.info("Sending pages")
                self.send_port.send_json(pages)
                pages = []
