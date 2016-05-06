import msgpack
from ..settings import SECRET_KEY
from .host import Host
from .list import DataList
from .url import URL
from .link import Link
from .pages import Page


class MessageDecodeError(Exception):
    pass


class MessageEncodeError(Exception):
    pass


class Message(object):
    """docstring for Message"""

    __slots__ = ["sender", "signature", "data"]
    TYPE = "MESSAGE"

    def __init__(self, sender=None, data_type=None, data=None, instance=None):
        super(Message, self).__init__()
        if instance is not None:
            self.decode(instance)
            return
        else:
            if sender is None or signature is None or data is None or data_type is None:
                raise ValueError("Not enough parameters")

            self.sender = sender
            self.signature = SECRET_KEY
            self.data = data
            self.data_type = data_type

    def decode(self, instance):
        values = None
        try:
            values = msgpack.unpackb(instance)
        except Exception:
            raise MessageDecodeError("Could not unpack instance")

        if not isinstance(values, dict):
            raise MessageDecodeError("Provided instance is not a dictionary")

        for key in ["sender", "signature", "data"]:
            if key not in values:
                raise KeyError("Message lacks information")

        self.sender = values["sender"]
        self.signature = values["signature"]
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

    def _decode_data(self, data):
        try:
            if self.data_type == "URLS":
                return URL(instance=data)
            elif self.data_type == "LINKS":
                return Link(instance=data)
            elif self.data_type == "HOSTS":
                return Host(instance=data)
            elif self.data_type == "PAGES":
                return Page(instance=data)
            elif self.data_type == "DATALISTS":
                return DataList(instance=data)
        except Exception as exc:
            raise MessageDecodeError("Could not decode data: {}".format(exc))
