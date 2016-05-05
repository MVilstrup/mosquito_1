class MetaDecodeError(Exception):
    pass


class MetaEncodeError(Exception):
    pass


class Meta(object):
    """docstring for Meta"""

    def __init__(self, arg):
        super(Meta, self).__init__()
        self.arg = arg

    def decode(self, instance):
        pass

    def encode(self):
        pass
