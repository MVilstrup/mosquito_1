#!/usr/bin/env python
# coding: utf-8
#
# Class used to recieve urls sent to the coordinater and handle them in the
# correct manner
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket

import zmq
import codecs
import asyncio
from mosquito.messages import URL, Host


class URLReceiver(object):

    def __init__(self, pull):
        context = zmq.Context()

        # Socket to receive urls from the managers
        self.pull = context.socket(zmq.PULL)
        self.pull.connect("tcp://localhost:{port}".format(port=pull))

    async def start(self):
        while True:
            url = Url(instance=self.pull.recv())
