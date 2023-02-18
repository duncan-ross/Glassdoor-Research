import socket
import re
import json
import os
from definitions import DATA_DIR


def local_ip():
    ips = [
        ip
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if not ip.startswith("127.")
    ][:1]

    if not ips:
        raise BaseException("Couldn't find local IP...")

    return ips[0]


def slugify(name):
    return re.sub("[^a-zA-Z0-9]+", "-", name)


def config(key):
    val = os.environ.get(key)

    if val and re.match("true", val, re.I):
        val = True
    elif val and re.match("false", val, re.I):
        val = False

    return val


def json_data(filename):
    file_path = "{}/{}.json".format(DATA_DIR, filename)

    if not os.path.exists(file_path):
        return {}

    with open(file_path) as f:
        return json.load(f)

def setall(d, keys, value):
    for k in keys:
        d[k] = value

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res
