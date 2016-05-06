from fetcher import Fetcher
from parser import Parser
from coordinator import Coordinator
from multiprocessing import Process
import zmq
import logging


def initiate_fetcher(receive_port, send_port):
    work_port = "tcp://127.0.0.1:5551"
    result_port = "tcp://127.0.0.1:6661"

    fetcher = Process(target=Fetcher,
                      args=(receive_port, work_port, result_port, send_port, 1))
    fetcher.start()

    return fetcher


def initiate_parser(receive_port, send_port):
    work_port = "tcp://127.0.0.1:5552"
    result_port = "tcp://127.0.0.1:6662"

    parser = Process(target=Parser,
                     args=(receive_port, work_port, result_port, send_port, 1))
    parser.start()

    return parser


def initiate_coordinator(roots, start_port, fetcher_port):
    front_port = "tcp://127.0.0.1:1112"
    back_port = "tcp://127.0.0.1:1113"

    coordinator = Process(
        target=Coordinator,
        args=(roots, start_port, fetcher_port, front_port, back_port))
    coordinator.start()

    return coordinator


if __name__ == "__main__":
    start_port = "tcp://127.0.0.1:1111"
    fetcher_port = "tcp://127.0.0.1:2222"
    parser_port = "tcp://127.0.0.1:4442"

    try:
        urls = []
        with open("top-1m.csv", "r") as domain_file:
            url = "http://www.{}"
            urls += [url.format(d.strip()) for d in domain_file.readlines()]

        # Give all start urls the same priority
        priority = [1 for i in range(len(urls))]

        # Zip together the list of priorities with the list of urls
        urls = zip(priority, urls)

        # Start coordinator and give it the seed URLs
        # Connect the coordinator to the fetcher
        coordinator = initiate_coordinator(roots=urls,
                                           start_port=start_port,
                                           fetcher_port=fetcher_port)

        # Start the fetcher and connect it to the coordinator and the parser
        fetcher = initiate_fetcher(fetcher_port, parser_port)

        # Start the parser and connect it to the fetcher and the coordinator
        parser = initiate_parser(parser_port, start_port)

        # Block forever
        coordinator.join()
        fetcher.join()
        parser.join()
    except KeyboardInterrupt:
        print("\nEXITING\n")
