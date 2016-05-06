# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket

import zmq
import logging


class Sink(object):

    def __init__(self, result_port, send_port, forward_pages):
        context = zmq.Context()

        self.logger = logging.getLogger('parser_sink')
        hdlr = logging.FileHandler('parser_sink.log')
        formatter = logging.Formatter(
            '%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)
        # This setting is used to check if there is a manager in the system
        # if there is a manager, the crawler is Focused otherwise it is not
        self.forward_pages = forward_pages

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

                if self.forward_pages:
                    message = {"page": page, "links": found_links}
                    extracted.append(message)
                else:
                    # Give all links equal priority
                    priority = [1 for i in range(len(found_links))]
                    found_links = list(zip(priority, found_links))
                    extracted.append(found_links)

                if len(extracted) >= 10:
                    self.logger.info("Sending extracted links")
                    self.send_port.send_json(extracted)
                    extracted = []
            except KeyboardInterrupt:
                print("Exiting sink")
                return
            except Exception as exc:
                self.logger.warning("{}".format(exc))
