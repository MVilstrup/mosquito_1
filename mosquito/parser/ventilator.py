#!/usr/bin/env python
# coding: utf-8
#
# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket

import zmq
import logging
from mosquito.messages import DataList


class Ventilator(object):

    def __init__(self, recieve_port, working_port):
        context = zmq.Context()

        logger = logging.getLogger('parser')
        hdlr = logging.FileHandler('parser.log')
        formatter = logging.Formatter(
            '%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        # Socket to receive lists of urls that should be sent
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(recieve_port)

        # Socket to send messages onto the workers to resolve the domain
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind(working_port)

        while True:
            try:
                message = Message(data_type="DATALIST",
                                  instance=self.receiver.recv())
                logger.info("Recieved pages")

                pages = message.data
                for page in pages:
                    self.sender.send(page.encode())
            except KeyboardInterrupt:
                print("Exiting ventilator")
                return
            except Exception as exr:
                logger.warning("EXCEPTION: {}".format(exr))
