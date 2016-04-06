import msgpack
from . import Cookies, Headers


class ResponseDecodeError(Exception):
    pass


class ResponseEncodeError(Exception):
    pass


class Response(object):
    """docstring for Response"""

    __slots__ = ["status", "reason", "method", "url", "cookies", "headers",
                 "content"]

    def __init__(self, response=None, url=None, instance=None):
        super(Response, self).__init__()
        if url is None and instance is None:
            raise ResponseDecodeError("Either a url or instance is needed")

        if instance is not None:
            self.decode(instance)
        elif response is not None:
            self.status = response.status  # Status-Code
            self.reason = response.reason  # Reason-Phrase
            self.method = response.method
            self.url = url
            self.cookies = Cookies(cookies=response.cookies)
            self.headers = Headers(headers=response.headers)
            if self.is_valid():
                self.content = await response.text()
            else:
                self.content = None
        else:
            # In this case, something went wrong with the crawler
            # This can be seen by the rest of the system with the 999 status
            self.status = 999
            self.url = url
            self.reason = None
            self.method = None
            self.cookies = None
            self.headers = None
            self.content = None


    def is_valid(self):
        return 200 <= int(self.status) < 300

    def is_redirect(self):
        return 300 <= int(self.status) < 400

    def client_error(self):
        return 400 <= int(self.status) < 500

    def server_error(self):
        return 500 <= int(self.status) < 600

    def crawler_error(self):
        return int(self.status) == 999

    def decode(self, instance):
        pass

    def encode(self):
        pass
