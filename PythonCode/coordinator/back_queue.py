from queue import FifoQueue
from mosquito.messages import URL
import asyncio
import sys
import time
import zmq

class BackQueue(object):
    """
    BackQueue used to be polite towards domains by not crawling them
    to frequently
    """
    def __init__(self, pull, push, queue_amount=10):
        super(BackQueue, self).__init__()
        assert queue_amount > 0

        self.queue_amount = queue_amount
        self.queues = []
        self.current_queue = 0
        for i in range(queue_amount):
            self.queues.append(FifoQueue())

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
            queue_id = hash(url.location) % self.queue_amount
            self.queues[queue_id].put_nowait(url)

    async def get(self):
        while True:
            url = self.queues[self.current_queue].get_nowait()
            self.queues[self.current_queue].task_done()
            self.current_queue += 1
            self.sender.send(url.encode())
