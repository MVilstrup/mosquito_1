#!/usr/bin/python
#

import asyncio
from joblib import Parallel, delayed
from asyncio import Queue
import numpy as np
from time import time
import socket


class MultiAsyncResolver(object):
    def __init__(self):
        """
        hosts: a list of hosts to resolve
        intensity: how many hosts to resolve at once
        """
        self.max_tasks = max_tasks
        self.resolved_hosts = {}
        self.start = time()
        self.difference = time()

    @asyncio.coroutine
    def work(self, hosts, max_tasks=50, loop=None):
        """ Resolves hosts and returns a dictionary of { 'host': 'ip' }. """
        loop = loop or asyncio.get_event_loop()
        queue = Queue(loop=loop)
        for host in hosts:
            self.queue.put_nowait(host)

        workers = [asyncio.Task(self.resolve(), queue)
                   for _ in range(max_tasks)]
        yield from self.queue.join()
        for w in workers:
            w.cancel()

    def resolve(self, queue):
        try:
            while True:
                host = yield from self.queue.get()
                ip = yield from self.fetch_ip(host)
                self.resolved_hosts[host] = ip
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def fetch_ip(self, host):
        ip = None
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            pass
        return ip

    def close(self):
        """Close resources."""
        end = time()
        print("It took {}.2f seconds to resolve {} hosts.".format(
            end - self.start, len(self.resolved_hosts.keys())))

    @asyncio.coroutine
    def resolve(self, hosts):
        """Run the crawler until all finished."""
        hosts = np.array(hosts, dtype="string_")
        task_iterator = (delayed(self.work)(host_block)
                         for host_block in np.split(hosts, n_jobs))

        result = parallelizer(tasks_iterator)

        # merging the output of the jobs
        return np.vstack(result)
