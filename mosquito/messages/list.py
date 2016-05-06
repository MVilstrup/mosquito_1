import msgpack
from . import Host, Link, URL
from .pages import Page


class DataListEncodeError(Exception):
    pass


class DataListDecodeError(Exception):
    pass


class DataList(object):
    """docstring for DataList"""

    __slots__ = ["elements", "_counter", "data_type"]
    TYPE = "DATALIST"

    def __init__(self, type=None, elements=None, instance=None):
        super(DataList, self).__init__()
        if elements is None and instance is None:
            raise ValueError(
                "DataList needs either some elements or an instance")

        if instance is not None:
            self.decode(instance)
        else:
            self.elements = elements
            self._counter = 0
            self.data_type = self._validate_type(type)


    def decode(self, instance):
        values = None
        try:
            values = msgpack.unpackb(instance)
        except Exception:
            raise DataListDecodeError("Could not unpack instance")

        if not isinstance(values, dict):
            raise DataListDecodeError("Provided instance is not a dictionary")

        if not "elements" in values or "data_type" not in values:
            raise DataListDecodeError("Data Keys doesn't match")

        self.data_type = values["data_type"]
        self.elements = [self._decode_element(e) for e in values["elements"]]
        self._counter = 0

    def encode(self):
        encoded_elements = []
        for element in elements:
            try:
                encoded = element.encode()
                encoded_elements.append(encoded)
            except Exception:
                raise DataListEncodeError("Could not encode all elements")

        values = {"data_type": self.data_type, "elements": encoded_elements}
        return msgpack.packb(values)

    def __iter__(self):
        return self

    def __next__(self):  # Python 3: def __next__(self)
        if self.counter > len(self.elements):
            self._counter = 0
            raise StopIteration
        else:
            element = self.elements[self._counter]
            self._counter += 1
            return element

    def _validate_type(self, type):
        type = type.upper()
        if type in ["URL", "LINK", "HOST", "PAGE", "DATALIST"]:
            return type

        raise ValueError("Unkown DataType: {}".format(type))

    def _decode_element(self, element):
        try:
            if self.data_type == "URLS":
                return URL(instance=element)
            elif self.data_type == "LINKS":
                return Link(instance=element)
            elif self.data_type == "HOSTS":
                return Host(instance=element)
            elif self.data_type == "PAGES":
                return Page(instance=element)
            elif self.data_type == "DATALISTS":
                return DataList(instance=element)
        except Exception as exc:
            raise DataListDecodeError("Could not decode element: {}".format(
                exc))
