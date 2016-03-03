from .datatypes import CaseInsensitiveDict
import re


def params_to_dict(self, params):
    """
    This method is used to alter string parameters into OrderedDicts to make it
    easier to work with the parameters of a url, as well as ensuring that two
    urls with the same parameters yet different ordering will be seen as equal
    """
    params = CaseInsensitiveDict()

    if not isinstance(params, str):
        raise ValueError("params_to_dict only works on string parameters")

    if params == "":
        return params

    if params.startswith("?"):
        params = params[1:]

    key_value_pairs = params.split("&")
    for parameter in key_value_pair:
        key, value = parameter.split("=")
        params[key] = value

    return params


def dict_to_params(self, param_dict):
    """
    This method is used to alter the parameters stored as an ordered dictionary
    back into a string.
    """
    if not isinstance(param_dict, CaseInsensitiveDict):
        raise ValueError("param_dict needs to be a CaseInsensitiveDict")

    if len(param_dict) == 0:
        return ""

    params = "?"
    for key, value in param_dict.lower_items():
        if not params.endswith("?"):
            params += "&"
        params += "{key}={value}".format(key=key, value)

    return params


def clean_protocol(self, protocol):
    return re.sub("\:\/\/", "", protocol).lower()


def clean_location(self, location):
    return re.sub("www\.", "", location).lower()


def clean_path(self, path):
    if path == "":
        return path

    if not path.startswith("/"):
        path = "/{}".format(path.lower())
    return path

def get_domain(self, url):
    """
    Method used to extract a domain from a given URL
    """
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
