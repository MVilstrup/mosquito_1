"""
This module defines the Link object used to represent actual links found on
pages. Links should not be confused with URLs which are a subset of the link
"""
import msgpack
import re
from url import URL


class LinkDecodeError(Exception):
    pass


class Link(object):

    __slots__ = ["url", "anchor_text", "classes_"]

    def __init__(self,
                 url=None,
                 anchor_text=None,
                 classes=None,
                 instance=None):
        if instance is not None:
            self.decode(instance)
        else:
            self.url = url
            self.anchor_text = anchor_text
            self.classes_ = classes
        if self.url is None:
            raise LinkDecodeError("Protocol is not  provided")
        elif not isinstance(self.url, URL):
            raise LinkDecodeError("url is not in correct format")
        if self.domain is None:
            raise LinkDecodeError("Domain is not  provided")

    def decode(self, instance):
        try:
            values = msgpack.unpackb(instance)
        except Exception:
            raise LinkDecodeError("Could not unpack instance")

        assert len(values) == 6
        assert values[0] is not None
        assert values[1] is not None
        assert values[3] is not None

        self.path = values[0].decode("utf-8")
        self.domain = self.clean_domain(values[1].decode("utf-8"))
        self.ip = values[2].decode("utf-8")
        self.path = values[3].decode("utf-8")
        self.anchor_text = values[4].decode("utf-8")
        self.classes_ = values[5].decode("utf-8")

    def encode(self):
        values = [self.protocol, self.domain, self.ip, self.path,
                  self.anchor_text, self.classes_]
        return msgpack.packb(values)

    def __eq__(self, other):
        return self.url == other.url and self.anchor_text == other.anchor_text\
                and self.ip == other.ip

    def __hash__(self):
        hash_ = hash(self.url)
        if self.anchor_text is not None:
            hash_ = hash_ ^ hash(self.anchor_text)
        if self.classes_ is not None:
            hash_ = hash_ ^ hash(self.classes_)
        return hash_

    def __repr__(self):
        return "Link(domain={}, url={}, anchor_text={}, classes_={})".format(
            self.domain, self.url, self.anchor_text, self.classes_)

    def classes(self):
        return self.classes_.split(" ")

