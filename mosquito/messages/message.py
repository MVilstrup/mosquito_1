import msgpack
from ..settings import SECRET_KEY
from .host import Host
from .list import DataList
from .url import URL
from .link import Link
from .pages import Page
import hashlib


class MessageDecodeError(Exception):
    pass


class MessageEncodeError(Exception):
    pass


class Message(object):
    """docstring for Message"""

    __slots__ = ["sender", "signature", "data", "data_type"]
    TYPE = "MESSAGE"

    def __init__(self, sender=None, data_type=None, data=None, instance=None):
        super(Message, self).__init__()
        self._check_data_type(data_type)
        if instance is not None:
            self.data_type = data_type
            self.decode(instance)
            return
        else:
            if sender is None or data is None or data_type is None:
                raise ValueError("Not enough parameters")

            self.sender = sender
            self.signature = SECRET_KEY
            self.data = data
            self.data_type = data_type

    def decode(self, instance):
        values = {}
        try:
            raw_values = msgpack.unpackb(instance)
            for key, value in raw_values.items():
                key = str(key, "utf-8")
                values[key] = value
        except Exception:
            raise MessageDecodeError("Could not unpack instance")

        if not isinstance(values, dict):
            raise MessageDecodeError("Provided instance is not a dictionary")

        for key in ["sender", "signature", "data"]:
            if key not in values:
                raise KeyError("Message lacks information")

        self.sender = str(values["sender"], "utf-8")
        self.signature = str(values["signature"], "utf-8")
        if not self.signature == SECRET_KEY:
            raise MessageDecodeError("Incorrect Signature")

        try:
            self.data = self._decode_data(values["data"])
        except Exception:
            raise MessageDecodeError("Could not decode message data")

    def encode(self):
        try:
            values = {"sender": self.sender,
                      "signature": self.signature,
                      "data": self.data.encode()}
            return msgpack.packb(values)
        except Exception as exc:
            raise MessageEncodeError("Message could not be encoded: {}".format(
                exc))

    def _check_data_type(self, data_type):
        if data_type not in ["URL", "LINK", "HOST", "PAGE", "DATALIST"]:
            raise ValueError("{} is not a supported DataType".format(data_type))

    def _decode_data(self, data):
        try:
            if self.data_type == "URL":
                return URL(instance=data)
            elif self.data_type == "LINK":
                return Link(instance=data)
            elif self.data_type == "HOST":
                return Host(instance=data)
            elif self.data_type == "PAGE":
                return Page(instance=data)
            elif self.data_type == "DATALIST":
                return DataList(instance=data)
        except Exception as exc:
            raise MessageDecodeError("Could not decode data: {}".format(exc))
