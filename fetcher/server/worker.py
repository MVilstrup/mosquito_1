# Task worker
# Connects PULL socket to tcp://localhost:5557
# Collects workloads from ventilator via that socket
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import asyncio

from multiprocessing import Process
from http import Request, Response

class Worker(object):
    # Process tasks forever
    def __init__(self, pull, push, loop=None):
        context = zmq.Context()
        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://localhost:{pull}".format(pull=pull))

        # Socket to send messages to
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://localhost:{push}".format(push=push))
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)

    @asyncio.coroutine
    def start(self):
        while True:
            request = Request(instance=self.receiver.recv())

            # Simple progress indicator for the viewer
            response = yield from self.fetch(request)
            sys.stdout.write('.')
            sys.stdout.flush()

            # Send results to sink
            self.sender.send(host.encode())

    @asyncio.coroutine
    def fetch(self, request):
        url = ""
        response = None
        try:
            response = yield from self.session.get(
                url, allow_redirects=False)
        except aiohttp.ClientError as client_error:
            pass
        correct_response = yield from self.handle_response(reponse)
        return correct_response


    @asyncio.coroutine
    def handle_response(self, response):
        pass

def start_worker():
    # Worker to go through all the hosts the first time
    primary_worker = Worker(pull=5557, push=5558)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(primary_worker.start())
    loop.close()


if __name__ == '__main__':
    for i in range(5):
        Process(target=start_worker).start()
