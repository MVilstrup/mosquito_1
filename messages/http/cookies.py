class CookiesDecodeError(Exception):
    pass


class CookiesEncodeError(Exception):
    pass


class Cookies(object):
    """docstring for Cookies"""

    def __init__(self, arg):
        super(Cookies, self).__init__()
        self.arg = arg

    def decode(self, instance):
        pass

    def encode(self):
        pass
