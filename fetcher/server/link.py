"""
This module defines the Link object used to represent actual links found on
pages. Links should not be confused with URLs which are a subset of the link
"""
import msgpack


class Link(object):

    __slots__ = ["protocol", "domain", "ip", "path", "anchor_text", "classes"]

    def __init__(self,
                 protocol=None,
                 domain=None,
                 ip=None,
                 path=None,
                 anchor_text=None,
                 classes=None,
                 instance=None):
        if instance is not None:
            self.decode(instance)
        else:
            self.protocol = protocol
            self.domain = domain
            self.ip = ip
            self.path = path
            self.anchor_text = anchor_text
            self.classes = classes

    def decode(self, instance):
        values = msgpack.unpackb(instance)
        assert len(values) == 6
        assert values[0] is not None
        assert values[1] is not None
        assert values[3] is not None

        self.path = values[0].decode("utf-8")
        self.domain = values[1].decode("utf-8")
        self.ip = values[2].decode("utf-8")
        self.path = values[3].decode("utf-8")
        self.anchor_text = values[4].decode("utf-8")
        self.classes = values[5].decode("utf-8")

    def encode(self):
        values = [self.protocol, self.domain, self.ip, self.path,
                  self.anchor_text, self.classes]
        return msgpack.packb(values)

    def __eq__(self, other):
        return self.domain == other.domain and self.path == other.path and \
                self.anchor_text == other.anchor_text and self.ip == other.ip

    def __hash__(self):
        hash_ = hash(self.protocol) ^ hash(self.domain) ^ hash(self.path)
        if self.ip is not None:
            hash_ = hash_ ^ hash(self.ip)
        if self.anchor_text is not None:
            hash_ = hash_ ^ hash(self.anchor_text)
        if self.classes is not None:
            hash_ = hash_ ^ hash(self.classes)
        return hash_

    def __repr__(self):
        return "Link(protocol={}, domain={}, ip={},\
                path={}, anchor_text={}, classes={})".format(
            self.protocol, self.domain, self.ip, self.path, self.anchor_text,
            self.classes)

    def to_string(self):
        host = self.ip
        if host is None:
            host = self.domain
        return "{protocol}www.{host}{path}".format(protocol=self.protocol,
                                                   host=host,
                                                   path=self.path)
