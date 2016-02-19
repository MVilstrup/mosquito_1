import msgpack


class Host(object):

    __slots__ = ["name", "ip"]

    def __init__(self, name=None, ip=None, instance=None):
        if instance is not None:
            self.decode(instance)
        else:
            self.name = name
            self.ip = ip

    def decode(self, instance):
        values = msgpack.unpackb(instance)
        assert len(values) == 2
        name, ip = values
        assert name is not None
        self.ip = ip.decode("utf-8") if ip is not None else None

    def encode(self):
        values = (self.name, self.ip)
        return msgpack.packb(values)

    def __eq__(self, other):
        return self.host == other.host and self.ip == other.ip

    def __hash__(self):
        if self.ip is not None:
            return hash(self.name) ^ hash(self.ip)
        return hash(self.name)

    def __repr__(self):
        return "Host(name={name}, ip={ip})".format(name=self.name, ip=self.ip)
