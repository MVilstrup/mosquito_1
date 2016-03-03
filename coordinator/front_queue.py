from queue import PriorityQueue
from mosquito.messages import URL
import asyncio
import sys
import time
import zmq

class FrontQueue(object):
    """
    FrontQueue used to be polite towards domains by not crawling them
    to frequently
    """
    def __init__(self pull, push):
        super(FrontQueue, self).__init__()
        self.queue = PriorityQueue()
        context = zmq.Context()
        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://localhost:{pull}".format(pull=pull))

        # Socket to send messages to
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://localhost:{push}".format(push=push))


    async def put(self):
        while True:
            url = Url(instance=self.receiver.recv())
            self.queue.put_nowait(url)

    async def get(self):
        while True:
            url = self.queue.get()
            self.sender.send(url.encode())
            self.queue.task_done()
