from collections import OrderedDict


class LocalCache(OrderedDict):
    """Dictionary with a finite number of keys.
    Older items expires first.
    """

    def __init__(self, limit=None):
        super(LocalCache, self).__init__()
        self.limit = limit

    def __setitem__(self, key, value):
        while len(self) >= self.limit:
            self.popitem(last=False)
        super(LocalCache, self).__setitem__(key, value)
