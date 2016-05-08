from .datatypes import CaseInsensitiveDict
import re
import sys


def params_to_dict(params):
    """
    This method is used to alter string parameters into OrderedDicts to make it
    easier to work with the parameters of a url, as well as ensuring that two
    urls with the same parameters yet different ordering will be seen as equal
    """

    if not isinstance(params, str):
        raise ValueError("params_to_dict only works on string parameters")

    param_dict = CaseInsensitiveDict()

    if params == "":
        return param_dict

    if params.startswith("?"):
        params = params[1:]

    key_value_pairs = params.split("&")
    for parameter in key_value_pair:
        key, value = parameter.split("=")
        param_dict[key] = value

    return param_dict


def dict_to_params(param_dict):
    """
    This method is used to alter the parameters stored as an ordered dictionary
    back into a string.
    """
    if param_dict is None:
        return ""

    if not isinstance(param_dict, CaseInsensitiveDict):
        raise ValueError("param_dict needs to be a CaseInsensitiveDict")

    if len(param_dict) == 0 or not param_dict:
        return ""

    params = "?"
    for key, value in param_dict.lower_items():
        if not params.endswith("?"):
            params += "&"
        params += "{key}={value}".format(key=key, value=value)

    return params


def clean_protocol(protocol):
    return re.sub("\:\/\/", "", protocol).lower()


def clean_location(location):
    return re.sub("www\.", "", location).lower()


def clean_path(path):
    if path == "":
        return path

    if not path.startswith("/"):
        path = "/{}".format(path.lower())

    return path.strip()


def get_domain(url):
    """
    Method used to extract a domain from a given URL
    """
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
