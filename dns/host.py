import msgpack
from random import randint


class Domain(object):

    __slots__ = ["name", "ip_addresses"]

    def __init__(self, name=None, ip_addresses=[], instance=None):
        if instance is not None:
            self.decode(instance)
        else:
            self.name = self._clean_domain(name)
            self.ip_addresses = ip_addresses

    def decode(self, instance):
        values = msgpack.unpackb(instance)
        assert len(values) == 2
        name, ip_addresses = values
        assert name is not None
        self.name = name

        ip_address_list = []
        for ip in ip_addresses:
            ip_address_list.append(ip.decode("utf-8"))
        self.ip_addresses = ip_address_list

    def add_ip(self, ip):
        self.ip_addresses.append(ip)

    def get_ip(self):
        """
        If multiple ip addresses are known for the same domain, a random domain
        is used.
        """
        return self.ip_addresses[randint(0, len(self.ip_addresses))]

    def encode(self):
        values = (self.name, self.ip_addresses)
        return msgpack.packb(values)

    def __eq__(self, other):
        return self.domain == other.domain

    def __hash__(self):
        _hash = hash(self.name)
        if self.ip_addresses is not None:
            for ip in self.ip_addresses:
            _hash = _hash ^ hash(self.ip)
        return _hash

    def __repr__(self):
        return "Host(name={name}, ip_addresses={ip_addresses})".format(
            name=self.name,
            ip_addresses=self.ip_addresses)

    def _clean_domain(self, domain):
        domain = re.sub(r"(http\:\/\/|https\:\/\/)", "", domain)
        return re.sub(r"www\.", "", domain)
