#!/usr/bin/env python
# coding: utf-8
#
# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket

import zmq
import codecs
import asyncio
from mosquito.messages import URL
from mosquito.messages.http import Request

class FetchVentilator(object):
    def __init__(self, push, pull, domains=None):
        context = zmq.Context()

        # Socket to receive all pull domains from the sink
        self.pull = context.socket(zmq.PULL)
        self.pull.connect("tcp://localhost:{port}".format(port=pull))
        self.domains = domains

        # Socket to send messages onto the workers to resolve the domain
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:{port}".format(port=push))

    async def forward(self):
        while True:
            url = URL(instance=self.pull.recv())
            request = Request(url=url)
            self.sender.send(request.encode())
