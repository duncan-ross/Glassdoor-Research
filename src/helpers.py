import socket
import re
import json
import os
from definitions import DATA_DIR
import difflib
import tqdm


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

def check_similarity(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()

def load(name):
    file_path = "{}".format(name)
    if not os.path.exists(file_path):
        return {}
    with open(file_path) as f:
        return json.load(f)

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


def extract_reviews(data):
    # Extract the reviews
    reviews = []
    for company in tqdm(data.values(), desc="Extracting reviews"):
        for review in company:
            if review == "PAGE_FAILURE":
                continue
            if review["pros"] is not None:
                reviews.append(review["pros"].split(".|!|?|\n"))
            if review["cons"] is not None:
                reviews.append(review["cons"].split(".|!|?|\n"))
            if review["advice"] is not None:
                reviews.append(review["advice"].split(".|!|?|\n"))

    # Filter out empty or None reviews
    reviews = [review for review in reviews if review]
    return reviews