# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket

import zmq
import logging

from mosquito.messages import DataList, Message


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
                found_links = DataList(instance=self.result_port.recv())
                extracted.append(found_links)

                if len(extracted) >= 10:
                    self.logger.info("Sending extracted links")
                    extracted_list = DataList(type="DATALISTS",
                                              elements=extracted)

                    message = message(data_type="DATALIST",
                                      sender="parser",
                                      data=extracted_list)
                    self.send_port.send(message.encode())
                    extracted = []
            except KeyboardInterrupt:
                print("Exiting sink")
                return
            except Exception as exc:
                self.logger.warning("{}".format(exc))
