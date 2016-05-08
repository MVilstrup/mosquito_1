"""
This module defines the URL object used to represent URLs found in links.
Links should not be confused with URLs which are a subset of the link
"""
import msgpack
import re
from urllib.parse import urlparse
from mosquito.utils.urls import (params_to_dict, dict_to_params, clean_protocol,
                                 clean_location, clean_path)
import sys


class URLDecodeError(Exception):
    pass


class URLEncodeError(Exception):
    pass


class URL(object):
    __slots__ = ["protocol", "location", "ip", "path", "parameters", "priority",
                 "fingerprint"]
    TYPE = "URL"

    def __init__(self, priority=1, ip=None, url=None, instance=None):
        if url is None and instance is None:
            raise URLDecodeError("Either a url or instance has to be provided")
        if instance is not None:
            self.decode(instance)
        else:
            if isinstance(url, bytes):
                url = url.decode("utf-8")
            parsed = urlparse(url)
            self.protocol = parsed.scheme
            self.location = parsed.netloc
            self.path = parsed.path
            self.parameters = params_to_dict(parsed.params)
            self.ip = ip
            self.priority = priority
            self.fingerprint = None

    @property
    def reversed(self):
        return self.to_string()[::-1]

    def decode(self, instance):
        values = {}
        try:
            raw_values = msgpack.unpackb(instance)
            for key, value in raw_values.items():
                key = str(key, "utf-8")
                values[key] = value
        except Exception:
            raise URLDecodeError("Could not unpack instance")

        try:
            self.protocol = clean_protocol(str(values["protocol"], "utf-8"))
            self.location = clean_location(str(values["location"], "utf-8"))
            self.path = clean_path(str(values["path"], "utf-8"))
            self.parameters = params_to_dict(str(values["parameters"], "utf-8"))
            self.priority = int(values["priority"])
            self.ip = values.get("ip")
            self.fingerprint = values.get("fingerprint")
        except KeyError:
            raise URLDecodeError("Could not unpack values, keys does not match")

    def encode(self):
        values = {"protocol": self.protocol,
                  "location": self.location,
                  "path": self.path,
                  "parameters": dict_to_params(self.parameters),
                  "priority": self.priority,
                  "ip": self.ip,
                  "TYPE": URL.TYPE,
                  "fingeprint": self.fingerprint}

        return msgpack.packb(values)

    def to_string(self, use_ip=False):
        if use_ip and self.ip is not None:
            host = self.ip
        else:
            host = self.location
        return "{protocol}://{host}{path}{params}".format(
            protocol=self.protocol,
            host=host,
            path=self.path,
            params=dict_to_params(self.parameters))

    def to_bytes(self):
        return self.to_string().encode("utf-8")

    def add_fingerprint(self, fingerprint):
        self.fingerprint = fingerprint

    def __eq__(self, other):
        return self.to_string() == other.to_string()

    def __hash__(self):
        return hash(self.to_string())

    def __str__(self):
        return self.to_string()

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __ge__(self, other):
        return self.priority >= other.priority

    def __repr__(self):
        string = "URL(protocol={}, location={}".format(self.protocol,
                                                       self.location)
        if self.path is not None and self.path != "":
            string += ", path={}".format(self.path)
        parameters = dict_to_params(self.parameters)
        if parameters is not None and parameters != "":
            string += ", parameters={}".format(parameters)
        string += ")"

        return string
