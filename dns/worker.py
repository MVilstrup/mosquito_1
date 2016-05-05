import sys
import time
import zmq
import logging
import socket
from threading import Thread
from Queue import Queue
import atexit

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('myapp.log')
formatter = logging.Formatter('%(asctime)-15s %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class Worker(object):

    def __init__(self, work_port, result_port, uid, loop=None, timeout=10):
        atexit.register(self._cleanup)
        context = zmq.Context()
        self.id = uid
        # Socket to receive messages on
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect(work_port)

        # Socket to send messages to
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect(result_port)
        self.timeout = timeout

        max_threads = 10
        self.work_queue = Queue(max_threads * 10)
        self.result_queue = Queue()

        self.threads = []
        for i in range(max_threads):
            thread = Thread(target=self._resolve)
            thread.start()
            self.threads.append(thread)

        try:
            while True:
                url = self.receiver.recv_string()
                self.work_queue.put(url)

                while not self.result_queue.empty():
                    ip = self.result_queue.get()
                    self.sender.send_json([url, ip])
        except KeyboardInterrupt:
            print("Exiting worker")
            return
        except:
            return

    def _resolve(self):
        while True:
            url = self.work_queue.get()
            try:
                ip_address = socket.gethostbyname_ex(url)
                if ip_address is not None:
                    self.result_queue.put(ip_address)
            except KeyboardInterrupt:
                break
            except Exception as exc:
                logger.info("ERROR: {} {}".format(url, exc))

    def _cleanup():
        timeout_sec = 5
        for t in self.threads:  # list of your processes
            p_sec = 0
            for second in range(timeout_sec):
                if t.poll() == None:
                    time.sleep(1)
                    p_sec += 1
                    if p_sec >= timeout_sec:
                        t.kill()  # supported from python 2.6
                        print 'cleaned up!'
