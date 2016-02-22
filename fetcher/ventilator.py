#!/usr/bin/env python
# coding: utf-8
#
# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import zmq
import codecs
from host import Host
import asyncio
from link import Link

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input


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

    @asyncio.coroutine
    def forward(self):
        while True:
            link = Link(instance=self.pull.recv())

            self.sender.send(request.encode())


    @asyncio.coroutine
    def create_request(self, link):
        pass


if __name__ == "__main__":
    domain_list = []
    with codecs.open('top.csv', "r", encoding="utf8") as domains:
        for line in domains.readlines():
            if len(domain_list) < 10000:
                domain_list.append(line.strip())

    print("domains: %i" % len(domain_list))
    print("Press Enter when the workers are ready: ")
    _ = raw_input()
    print("Sending tasks to workers...")
    server = FetchVentilator(push=5557, pull=5559, domains=domain_list)
    loop = asyncio.get_event_loop()
    methods = [asyncio.Task(server.send()), asyncio.Task(server.receive())]
    loop.run_until_complete(asyncio.gather(*methods))
    loop.close()
    print("All Domains Sent")
