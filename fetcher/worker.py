import sys
import time
import zmq
import asyncio

from multiprocessing import Process
from mosquito.messages.http import Request, Response


class Worker(object):
    def __init__(self, pull, push, loop=None, timeout=10):
        context = zmq.Context()
        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://localhost:{pull}".format(pull=pull))

        # Socket to send messages to
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://localhost:{push}".format(push=push))
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.timeout = timeout

    async def start(self):
        while True:
            request = Request(instance=self.receiver.recv())

            # Simple progress indicator for the viewer
            response = await self.fetch(request)
            if response is None:
                continue

            sys.stdout.write('.')
            sys.stdout.flush()

            # Send results to sink
            self.sender.send(host.encode())


    async def fetch(self, request):
        url = request.url
        headers = request.headers
        cookies = request.cookies

        response = None
        try:
            with aiohttp.Timeout(self.timeout):
                async with self.session.get(url.to_string(),
                                            headers=headers,
                                            cookies=cookies,
                                            allow_redirects=False) as response:
                    return Response(response=response, url=url)
        except Exception:
            return Response(url=url)

def start_worker():
    # Worker to go through all the hosts the first time
    primary_worker = Worker(pull=5557, push=5558)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(primary_worker.start())
    loop.close()


if __name__ == '__main__':
    for i in range(5):
        Process(target=start_worker).start()
