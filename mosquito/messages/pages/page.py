import msgpack
from mosquito.messages import URL


class PageDecodeError(Exception):
    pass


class PageEncodeError(Exception):
    pass


class Page():

    __slots__ = ["_body", "url", "_encoding"]

    TYPE = "PAGE"

    def get_body(self):
        raise NotImplementedError('{} does not override get_body()!'.format(
            self.TYPE))

    def get_links(self):
        raise NotImplementedError('{} must override get_links()!'.format(
            self.TYPE))

    def get_text(self):
        raise NotImplementedError('{} must override get_text()!'.format(
            self.TYPE))

    def decode(self, instance):
        values = {}
        try:
            raw_values = msgpack.unpackb(instance)
            for key, value in raw_values.items():
                key = str(key, "utf-8")
                values[key] = value
        except Exception:
            raise PageDecodeError("Could not unpack instance")

        if "encoding" not in values or "body" not in values or "url" not in values:
            raise PageDecodeError(
                "Could not unpack values, keys does not match")

        if not "TYPE" in values or str(values["type"], "utf-8") != self.TYPE:
            raise PageDecodeError("The page type does not match the content")

        try:
            self._encoding = str(values["encoding"])
            self._body = str(values["body"], encoding if encoding is not None
                             else "utf-8")
            self.url = URL(instance=values["url"])
        except KeyError:
            raise PageDecodeError(
                "Could not unpack values, keys does not match")

    def encode(self):
        values = {"body": self._body,
                  "url": self.url.encode(),
                  "encoding": self._encoding,
                  "TYPE": self.TYPE}

        return msgpack.packb(values)
