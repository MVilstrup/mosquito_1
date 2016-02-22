import msgpack
from random import randint

class HostDecodeError(Exception):
    pass

class HostEncodeError(Exception):
    pass

class Host(object):

    __slots__ = ["domain", "ip_addresses"]

    def __init__(self, domain=None, ip_addresses=None, instance=None):
        if instance is not None:
            self.decode(instance)
        else:
            self.domain = self._clean_host(domain)
            self.ip_addresses = ip_addresses

    def decode(self, instance):
        values = msgpack.unpackb(instance)
        if not isinstance(values, dict):
            raise HostDecodeError("Provided instance is not a dictionary")
        if values[b"domain"] is None:
            raise HostDecodeError("Domain was not provided")

        try:
            domain = values[b"domain"]
            ip_addresses = values[b"ip_addresses"]
            self.domain = self._clean_host(domain.decode("utf-8"))
            
            if ip_addresses:
                ip_address_list = []
                for ip in ip_addresses:
                    ip_address_list.append(ip.decode("utf-8"))
                self.ip_addresses = ip_address_list
        except KeyError:
            raise HostDecodeError("Could not unpack values, keys do not match")



    def encode(self):
        if self.domain is None or self.domain == "":
            raise HostEncodeError("Domain should always be present")

        IPs = self.ip_addresses if self.ip_addresses is not None else None
        values = {"domain":self.domain,"ip_addresses": IPs}

        return msgpack.packb(values)

    def add_ip(self, ip):
        self.ip_addresses.append(ip)

    def get_ip(self):
        """
        If multiple ip addresses are known for the same host, a random ip
        is used.
        """
        return self.ip_addresses[randint(0, len(self.ip_addresses))]


    def __eq__(self, other):
        return self.host == other.host

    def __hash__(self):
        _hash = hash(self.domain)
        if self.ip_addresses is not None:
            for ip in self.ip_addresses:
            _hash = _hash ^ hash(self.ip)
        return _hash

    def __repr__(self):
        return "Host(domain={domain}, ip_addresses={ip_addresses})".format(
            domain=self.domain,
            ip_addresses=self.ip_addresses)

    def _clean_host(self, host):
        host = re.sub(r"(http\:\/\/|https\:\/\/)", "", host)
        host = re.sub(r"www\.", "", host)
        return host.split("/")[0]
