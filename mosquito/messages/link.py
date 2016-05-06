"""
This module defines the Link object used to represent actual links found on
pages. Links should not be confused with URLs which are a subset of the link
"""
import msgpack
import re
from .url import URL


class LinkDecodeError(Exception):
    pass


class LinkEncodeError(Exception):
    pass


class Link(object):

    __slots__ = ["url", "anchor_text", "classes"]
    TYPE = "LINK"

    def __init__(self, url=None, anchor_text=None, classes=None, instance=None):
        if instance is not None:
            self.decode(instance)
        else:
            self.url = url
            self.anchor_text = anchor_text
            self.classes = classes
        if self.url is None:
            raise LinkDecodeError("URL is not  provided")
        elif not isinstance(self.url, URL):
            raise LinkDecodeError("URL is not in correct format")

    def decode(self, instance):
        try:
            values = msgpack.unpackb(instance)
        except Exception:
            raise LinkDecodeError("Could not unpack instance")

        if not isinstance(values, dict):
            raise LinkDecodeError("Provided instance is not a dictionary")

        try:
            self.url = URL(instance=values[b"url"])
            self.anchor_text = values[b"anchor"].decode("utf-8")
            self.classes = values[b"classes"].decode("utf-8")
        except KeyError:
            raise LinkDecodeError(
                "Could not unpack values, keys does not match")

    def encode(self):
        values = {"url": self.url.encode(),
                  "anchor": self.anchor_text,
                  "classes": self.classes}
        return msgpack.packb(values)

    def __eq__(self, other):
        return self.url == other.url and self.anchor_text == other.anchor_text\
                and self.ip == other.ip

    def __hash__(self):
        hash_ = hash(self.url)
        if self.anchor_text is not None:
            hash_ = hash_ ^ hash(self.anchor_text)
        if self.classes is not None:
            hash_ = hash_ ^ hash(self.classes)
        return hash_

    def __repr__(self):
        return "Link(domain={}, url={}, anchor_text={}, classes={})".format(
            self.domain, self.url, self.anchor_text, self.classes)
