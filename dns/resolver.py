#!/usr/bin/python
#

import asyncio
from asyncio import Queue
from time import time
import socket


class AsyncResolver(object):
    def __init__(self, hosts, max_tasks=50, loop=None):
        """
        hosts: a list of hosts to resolve
        intensity: how many hosts to resolve at once
        """

        self.loop = loop or asyncio.get_event_loop()
        self.max_tasks = max_tasks
        self.resolved_hosts = {}
        self.queue = Queue(loop=self.loop)
        for host in hosts:
            self.queue.put_nowait(host)
        self.start = time()
        self.difference = time()

    @asyncio.coroutine
    def work(self):
        """ Resolves hosts and returns a dictionary of { 'host': 'ip' }. """
        try:
            while True:
                host = yield from self.queue.get()
                self.queue.task_done()

                try:
                    ip = yield from self.fetch_ip(host)
                    self.resolved_hosts[host] = ip
                except socket.gaierror:
                    resolved_hosts[host] = None
                self.std_out()
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def fetch_ip(self, host):
        return socket.gethostbyname(host)

    def close(self):
        """Close resources."""
        end = time()
        print("It took {}.2f seconds to resolve {} hosts.".format(
            end - self.start, len(self.resolved_hosts.keys())))

    def std_out(self):
        end = time()
        if end - self.difference > 10:
            print("It took {} seconds to resolve {} hosts.".format(
                end - self.start, len(self.resolved_hosts.keys())))
            self.difference = end - self.start

    @asyncio.coroutine
    def resolve(self):
        """Run the crawler until all finished."""
        workers = [asyncio.Task(self.work(),
                                loop=self.loop) for _ in range(self.max_tasks)]
        yield from self.queue.join()
        for w in workers:
            w.cancel()
