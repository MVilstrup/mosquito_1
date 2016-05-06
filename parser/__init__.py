# modified fetch function with semaphore
import zmq
from multiprocessing import Process

import logging
from .ventilator import Ventilator
from .worker import Worker
from .sink import Sink

logger = logging.getLogger('parser')
hdlr = logging.FileHandler('parser.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Parser(object):
    """docstring for Parser"""

    def __init__(self,
                 recieve_port,
                 work_port,
                 result_port,
                 send_port,
                 max_workers=100,
                 forward_pages=False):

        super(Parser, self).__init__()

        # List of all the processes
        processes = []

        # Start ventilator to recieve urls to retreive
        ventilator = Process(target=Ventilator, args=(recieve_port, work_port))
        ventilator.start()
        processes.append(ventilator)

        # Start the Sink in order to forward the result of the workers
        sink = Process(target=Sink, args=(result_port, send_port, forward_pages))
        sink.start()

        # Start all the workers in order to start the fetching
        for i in range(max_workers):
            worker = Process(target=Worker, args=(work_port, result_port, i))
            worker.start()
            processes.append(worker)

        logger.info("Fully started up")

        for process in processes:
            process.join()
