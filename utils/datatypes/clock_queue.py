from queue import FifoQueue


class ClockQueue(object):
    """
    A Queue used to control actions based on time intervals
    """

    def __init__(self,
                 time_steps,
                 days=None,
                 hours=None,
                 minutes=None,
                 seconds=None):
        super(ClockQueue, self).__init__()

        self.time_steps = time_steps
        self._queues = []
        self.scheduler = None
        self.current_queue = 0

        # Add the specified amount of FifoQueues
        for range(time_steps):
            self._queues.append(FifoQueue())

        self._set_timer(days, hours, minutes, seconds)

    def _set_timer(self, days=None, hours=None, minutes=None, seconds=None):
        """
        Sets a timer that runs in the background and changes the queue from
        which items are retrieved according to the chosed interval.
        """
        pass

    def _change_queue(self):
        self.current_queue = (self.current_queue + 1) % self.time_steps

    def put(self, key, element):
        """
        Put inserts elements into the queue based on a hashed key. This means that
        the items inserted with the same key will always be put into the same queue
        and thus be retrieved in a cronological order
        """
        self._queues[hash(key) % time_steps].put(element)

    def put_nowait(self):
        self._queues[hash(key) % time_steps].put_nowait(element)

    def get(self, *args):
        """
        Get can be called continuesly without being concerned which queue one
        actually gets the elements from
        """
        return self._queues[self.current_queue].get_nowait()


    def qsize(self):
        size = 0
        for queue in self._queues:
            size += queue.size()
        return size

    def empty(self):
        for queue in self._queues:
            if not queue.empty():
                return False
        return True


    def join(self):
        for queue in self._queues:
            queue.join()
