class HeadersDecodeError(Exception):
    pass


class HeadersEncodeError(Exception):
    pass


class Headers(object):
    """docstring for Headers"""

    def __init__(self, arg):
        super(Headers, self).__init__()
        self.arg = arg

    def decode(self, instance):
        pass

    def encode(self):
        pass
