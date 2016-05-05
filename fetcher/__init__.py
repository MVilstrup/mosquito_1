# modified fetch function with semaphore
import zmq
from multiprocessing import Process

import logging
from .ventilator import Ventilator
from .worker import Worker
from .sink import Sink

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('myapp.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Fetcher(object):
    """docstring for Fetcher"""

    def __init__(self,
                 recieve_port,
                 work_port,
                 result_port,
                 send_port,
                 max_workers=100):
        super(Fetcher, self).__init__()

        # List of all the processes
        processes = []

        # Start ventilator to recieve urls to retreive
        ventilator = Process(target=Ventilator, args=(recieve_port, work_port))
        ventilator.start()
        processes.append(ventilator)

        # Start the Sink in order to forward the result of the workers
        sink = Process(target=Sink, args=(result_port, send_port))
        sink.start()

        # Start all the workers in order to start the fetching
        for i in range(max_workers):
            worker = Process(target=Worker, args=(work_port, result_port, i))
            worker.start()
            processes.append(worker)

        for process in processes:
            process.join()


if __name__ == "__main__":
    receive_port = "tcp://127.0.0.1:4444"
    work_port = "tcp://127.0.0.1:5555"
    result_port = "tcp://127.0.0.1:6666"
    send_port = "tcp://127.0.0.1:7777"

    worker = Process(target=Fetcher,
                     args=(receive_port, work_port, result_port, send_port, 1))
    worker.start()

    urls = []
    with open("top-1m.csv", "r") as domain_file:
        url = "http://www.{}"
        urls += [url.format(d.strip()) for d in domain_file.readlines()]

    n = 1000
    url_lists = [urls[i:i + n] for i in range(0, len(urls), n)]
    logger.info("Sending urls")
    # Socket to send messages onto the workers to resolve the domain

    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    sender.bind(receive_port)
    for urls in url_lists:
        sender.send_json(urls, flags=0)

    receiver = context.socket(zmq.PULL)
    receiver.connect(send_port)
    while True:
        pages = receiver.recv_json()
        for page in pages:
            print(page[:10])

    worker.join()
