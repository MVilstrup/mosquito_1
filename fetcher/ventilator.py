#!/usr/bin/env python
# coding: utf-8
#
# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket

import zmq
import logging

logger = logging.getLogger('fetcher')
hdlr = logging.FileHandler('fetcher.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Ventilator(object):

    def __init__(self, recieve_port, working_port):
        context = zmq.Context()

        # Socket to receive lists of urls that should be sent
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(recieve_port)

        # Socket to send messages onto the workers to resolve the domain
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind(working_port)

        while True:
            try:
                urls = self.receiver.recv_json()
                logger.info("Recieved urls")
                for url in urls:
                    self.sender.send_string(url)
            except KeyboardInterrupt:
                print("Exiting ventilator")
                return
            except:
                pass
