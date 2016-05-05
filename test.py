from fetcher import Fetcher
from parser import Parser
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


if __name__ == "__main__":
    fetcher_port = "tcp://127.0.0.1:4441"
    parser_port = "tcp://127.0.0.1:4442"
    result_port = "tcp://127.0.0.1:7772"

    try:
        fetcher = initiate_fetcher(fetcher_port, parser_port)
        parser = initiate_parser(parser_port, result_port)

        urls = []
        with open("top-1m.csv", "r") as domain_file:
            url = "http://www.{}"
            urls += [url.format(d.strip()) for d in domain_file.readlines()]

        n = 1000
        url_lists = [urls[i:i + n] for i in range(0, len(urls), n)]

        # Socket to send links to the fetcher to retrieve the pages
        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.bind(fetcher_port)
        print("SENDING URLS")
        for urls in url_lists:
            sender.send_json(urls, flags=0)

        # Create socket to listen to the parsed links
        receiver = context.socket(zmq.PULL)
        receiver.connect(result_port)
        print("WAITING TO RECEIVE URLS")
        while True:
            found_links = receiver.recv_json()
            for link in found_links:
                print("Found: {}".format(link))

        # Block forever
        fetcher.join()
        parser.join()
    except KeyboardInterrupt:
        print("\nEXITING\n")
