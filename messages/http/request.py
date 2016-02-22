from utils import to_bytes
from headers import Headers
import msgpack

class RequestDecodeError(Exception):
    pass

class RequestEncodeError(Exception):
    pass

class Request(object):

    __slots__ = ["url", "method", "body", "cookies", "headers", "meta",
                 "encoding"]

    def __init__(self, url,
                 encoding="utf-8",
                 method='GET',
                 headers=None,
                 body=None,
                 cookies=None,
                 meta=None):

        assert isinstance(url, str)
        self.url = url
        self.encoding = encoding
        self.method = str(method).upper()
        self._set_body(body)

        try:
            self.cookies = Cookies(
                instance=cookies) if cookies is not None else None
        except CookiesDecodeError:
            self.cookies = None

        try:
            self.headers = Headers(instance=headers) if headers is not None else None
        except HeadersDecodeError:
            self.headers = None

        try:
            self.meta = Meta(instance=meta) if meta is not None else None
        except MetaDecodeError:
            self.meta = None


    def _set_body(self, body):
        if body is None:
            self._body = b''
        else:
            self._body = to_bytes(body, self.encoding)

    @property
    def encoding(self):
        return self._encoding

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    def decode(self, instance):
        values = msgpack.unpackb(instance)
        assert isinstance(values, dict)
        base = values.get(b'base')
        assert isinstance(base, set)
        assert base[0] is not None
        assert base[1] is not None
        assert base[2] is not None

        self.url = base[0].decode("utf-8")
        self.encoding = base[1].decode("utf-8")
        self.method = base[2].decode("utf-8").upper()
        self._body = base[3]

        try:
            self.meta = Meta(instance=values.get(b'meta'))
        except MetaDecodeError:
            self.meta = None
        try:
            self.cookies = Cookies(instance=values.get(b'cookies'))
        except CookiesDecodeError:
            self.cookies = None
        try:
            self.headers = Headers(instance=values.get(b'headers'))
        except HeadersDecodeError:
            self.headers = None

    def encode(self):
        values = [self.protocol, self.domain, self.ip, self.path,
                  self.anchor_text, self.classes]
        return msgpack.packb(values)
