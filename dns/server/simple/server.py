#!/usr/bin/env python
# coding: utf-8

from client_thread import ClientThread
import socket
import sys
from timeout import timeout, TimeoutError


class DNSServer(object):
    def __init__(self, port):
        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpsock.bind(("", port))
        self.listen_threads = []

    def listen(self, backlog=5):
        try:
            print("Listening...")
            while True:
                self.tcpsock.listen(backlog)
                (clientsocket, (ip, port)) = self.tcpsock.accept()
                client = ClientThread(ip, port, clientsocket)
                client.start()
                self.listen_threads.append(client)

                # Iterate through all Threads to ensure they are closed
                for thread in self.listen_threads:
                    if not thread.isAlive():
                        self.listen_threads.remove(thread)
                        thread.join()

        except KeyboardInterrupt:
            print('Ctrl+C pressed... Shutting Down')
        except Exception:
            print('Exception caught: {}\nClosing...'.format(sys.exc_info()))
        finally:
            # Clear the list of threads, giving each thread 1 second to finish
            for thread in self.listen_threads:
                thread.join(1.0)

            # Close the socket once we're done with it
            self.tcpsock.close()

    def resolve(self, host):
        """
        The runtime is defined as an exponential function.

        --- Allowed runtime ---
        First Attempt: 3 Seconds
        Second Attempt: 9 Seconds
        Third Attempt: 27 Seconds
        Fourth Attempt: 81 Seconds
        After this, the Host is concluded to be None
        """
        while self.attempt <= 4:
            with timeout(seconds=3 ** self.attempt):
                try:
                    print("IP-Address : ", socket.gethostbyname(host))
                except socket.gaierror:
                    print("Could not find IP Address")
                    return
                except TimeoutError:
                    self.attempt += 1
                    print(host, "timed out... Retrying")
