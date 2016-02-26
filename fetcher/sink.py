# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket

import zmq
import asyncio
import sys
from mosquito.messages.http import Response


class Sink(object):
    def __init__(self, pull, push):
        context = zmq.Context()

        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://*:{port}".format(port=pull))

        # Socket to reschedule domains that timed out
        self.finish = context.socket(zmq.PUSH)
        self.finish.bind("tcp://*:{port}".format(port=push))

    async def start(self):
        # Process 100 confirmations
        tasks_done = 0
        while True:
            response = Response(instance=self.receiver.recv())
            self.finish.send(response.encode())


if __name__ == '__main__':
    # Worker to go through all the hosts the first time
    sink = Sink(pull=5558, push=5559)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(sink.start())
    loop.close()
