import zmq
from .back_queue import BackQueue
from .front_queue import FrontQueue
from multiprocessing import Process
import logging

from mosquito.messages import DataList


class Coordinator(object):
    """
    Coordinator used to keep track of all the URLs seen and what URLs to crawl
    next
    """

    def __init__(self, roots, inbound_port, outbound_port, front_port,
                 back_port):
        logger = logging.getLogger('coordinator')
        hdlr = logging.FileHandler('coordinator.log')
        formatter = logging.Formatter(
            '%(asctime)-15s %(levelname)s : %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        # Initialize FrontQueue used to prioritize what urls to visit next
        front_queue = Process(target=FrontQueue,
                              args=(inbound_port, front_port, roots))
        front_queue.start()

        # Initialize BackQueue used to be kind to all domains by limiting the
        # amount of request sent to each domain at a time
        batch_size = 1000
        back_queue = Process(target=BackQueue,
                             args=(outbound_port, back_port, batch_size))
        back_queue.start()

        context = zmq.Context()
        # Socket used to receive requests for new URLs from the BackQueue
        self.back_server = context.socket(zmq.REP)
        self.back_server.bind(back_port)
        logger.info("Connected BackQueue to: {}".format(back_port))

        # Socket used to request a new batch of URLs from the FrontQueue
        self.front_client = context.socket(zmq.REQ)
        self.front_client.connect(front_port)
        logger.info("Connected FrontQueue to: {}".format(front_port))

        while True:
            # Wait for a request for urls from the BackQueue
            request = self.back_server.recv_string()

            # Check the request is proper
            if not request or request != "REQUEST":
                continue

            # Forward the request to the FrontQueue to retrieve the URLs
            self.front_client.send_string(request)

            # Wait for the FrontQueue to respond
            url_list = DataList(instance=self.front_client.recv())

            # Check all URLs in the response and send them to the BackQueue
            urls = self.check_urls(url_list)
            if urls:
                self.back_server.send(urls.encode())

        front_queue.join()
        back_queue.join()

    def check_urls(self, urls):
        return urls
