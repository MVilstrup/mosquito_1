from threading import Thread
from queue import Queue
import sys
import requests
import asyncio
import zmq
from multiprocessing import Process
import time

concurrent = 50


def worker(wrk_num):
    # Initialize a zeromq context
    context = zmq.Context()

    # Set up a channel to receive work from the ventilator
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://127.0.0.1:5557")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch(receiver))
    loop.close()


@asyncio.coroutine
def fetch(receiver):
    with requests.Session() as s:
        while True:
            work_message = receiver.recv_json()
            url = work_message["url"]
            yield from getStatus(s, url)


@asyncio.coroutine
def getStatus(session, url):
    try:
        response = yield from get(session, url)
        sys.stdout.write('{}    {}\n'.format(response.status_code, url))
        sys.stdout.flush()
    except:
        sys.stdout.write('Error    {}\n'.format(url))
        sys.stdout.flush()


@asyncio.coroutine
def get(session, url):
    return session.get(url)


def ventilator():
    # Initialize a zeromq context
    context = zmq.Context()

    # Set up a channel to send work
    ventilator_send = context.socket(zmq.PUSH)
    ventilator_send.bind("tcp://127.0.0.1:5557")

    # Give everything a second to spin up and connect
    time.sleep(1)

    # Send the numbers between 1 and ten thousand as work messages
    with open('french_ip.csv') as _file:
        for url in _file.readlines()[:1000]:
            work_message = {'url': url.strip()}
            ventilator_send.send_json(work_message)

    time.sleep(1)


if __name__ == "__main__":
    try:
        # Create a pool of workers to distribute work to
        context = zmq.Context()
        worker_pool = range(concurrent)
        for wrk_num in range(len(worker_pool)):
            Process(target=worker, args=(wrk_num,)).start()

        # Start the ventilator!
        ventilator = Process(target=ventilator, args=())
        ventilator.start()
    except KeyboardInterrupt:
        sys.exit[0]
