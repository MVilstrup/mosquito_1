"""
This module defines the URL object used to represent URLs found in links.
Links should not be confused with URLs which are a subset of the link
"""
import msgpack
import re
from urllib.parse import urlparse
from mosquito.utils.urls import (params_to_dict, dict_to_params, clean_protocol,
                                 clean_location, clean_path, reverse)


class URLDecodeError(Exception):
    pass


class URLEncodeError(Exception):
    pass


class URL(object):
    __slots__ = ["protocol", "location", "path", "parameters", "reversed"]

    def __init__(self, url=None, instance=None):
        if url is None and instance is None:
            raise URLDecodeError("Either a url or instance has to be provided")
        if instance is not None:
            self.decode(instance)
        else:
            parsed = urlparse(url)
            self.protocol = parsed.scheme
            self.location = parsed.netloc
            self.path = parsed.path
            self.parameters = params_to_dict(parsed.params)
            self.reversed = reverse(url)

    def decode(self, instance):
        try:
            values = msgpack.unpackb(instance)
        except Exception:
            raise URLDecodeError("Could not unpack instance")

        if not isinstance(values, dict):
            raise URLDecodeError("Provided instance is not a dictionary")

        try:
            self.protocol = clean_protocol(values[b"protocol"].decode("utf-8"))
            self.location = clean_location(values[b"location"].decode("utf-8"))
            self.path = clean_location(values[b"path"].decode("utf-8"))
            self.parameters = params_to_dict(values[b"parameters"].decode(
                "utf-8"))
            self.reversed = reverse(self.to_string())
        except KeyError:
            raise URLDecodeError("Could not unpack values, keys does not match")

    def encode(self, instance):
        values = {"protocol": self.protocol,
                  "location": self.location,
                  "path": self.path,
                  "parameters": dict_to_params(self.params)}

        return msgpack.packb(values)

    def to_string(self):
        return "{protocol}://www.{host}{path}{params}".format(
            protocol=self.protocol,
            host=self.location,
            path=self.path,
            params=dict_to_params(self.parameters))

    def __eq__(self, other):
        return self.reversed == other.reversed

    def __hash__(self):
        return hash(self.to_string())

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return "URL(protocol={}, location={}, path={}, params={})".format(
            self.protocol, self.location, self.path,
            dict_to_params(self.parameters))
