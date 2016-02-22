#!/usr/bin/env python
# coding: utf-8
#
# Task ventilator
# Binds PUSH socket to tcp://localdomain:5557
# Sends batch of tasks to workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import zmq
import codecs
from domain import Domain
import asyncio

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input


class DNSServer(object):
    def __init__(self, push, pull, domains=None):
        context = zmq.Context()

        # Socket to send messages onto the workers to resolve the domain
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://*:{port}".format(port=push))

        # Socket to receive all resolved domains from the sink
        self.resolved = context.socket(zmq.PULL)
        self.resolved.connect("tcp://localdomain:{port}".format(port=pull))
        self.domains = domains

    @asyncio.coroutine
    def send(self):
        domains_sent = 0
        for domain in self.domains:
            domains_sent += 1
            domain = Domain(name=domain)
            self.sender.send(domain.encode())

    @asyncio.coroutine
    def receive(self):
        done = 0
        with codecs.open("domains_with_ip.csv", "w", encoding="utf-8") as _file:
            while True:
                domain = Domain(instance=self.resolved.recv())
                print(done, domain.name, domain.ip "\n")
                done += 1
                _file.write("{} {}  {}  {}  {}".format(
                    done, domain.name, domain.ip, domain.attempt, "\n"))


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
    server = DNSServer(push=5557, pull=5559, domains=domain_list)
    loop = asyncio.get_event_loop()
    methods = [asyncio.Task(server.send()), asyncio.Task(server.receive())]
    loop.run_until_complete(asyncio.gather(*methods))
    loop.close()
    print("All Domains Sent")
