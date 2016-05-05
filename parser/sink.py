# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket

import zmq
import logging

logger = logging.getLogger('parser')
hdlr = logging.FileHandler('parser.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Sink(object):

    def __init__(self, result_port, send_port):
        context = zmq.Context()

        # Socket to receive messages on
        self.result_port = context.socket(zmq.PULL)
        self.result_port.bind(result_port)

        # Socket to reschedule domains that timed out
        self.send_port = context.socket(zmq.PUSH)
        self.send_port.bind(send_port)
        self._forward()

    def _forward(self):
        extracted = []
        while True:
            try:
                page, found_links = self.result_port.recv_json()
                extracted.append(found_links)

                if len(extracted) >= 10:
                    logger.info("Sending extracted links")
                    self.send_port.send_json(extracted)
                    extracted = []
            except KeyboardInterrupt:
                print("Exiting sink")
                return
            except:
                pass
