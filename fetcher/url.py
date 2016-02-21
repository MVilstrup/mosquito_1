"""
This module defines the URL object used to represent URLs found in links. 
Links should not be confused with URLs which are a subset of the link
"""
import msgpack
import re


class URL(object):

    __slots__ = ["protocol", "ip", "path"]

    def __init__(self, protocol=None, ip=None, path=None, instance=None):
        if instance is not None:
            self.decode(instance)

    def decode(self, instance):
        pass

    def encode(self, instance):
        pass

    def to_string(self):
        return "{protocol}www.{host}{path}".format(protocol=self.protocol,
                                                   host=self.ip,
                                                   path=self.path)

    def reverse(self):
        return self.to_string()[::-1]

    def __eq__(self, other):
        return self.reverse_string() == other.reverse_string()

    def __hash__(self):
        return hash(self.to_string())

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return "URL(protocol={}, ip={}, path={})".format(self.protocol,
                                                         self.ip, self.path)
