import socket
import re
import json
import os
from definitions import DATA_DIR
import difflib


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

def main2():
    output = {}
    companies_map = json_data("companies_map")
    for i, (name, info) in enumerate(companies_map.items()):
        url = info["reviews_url"].split('.htm?')[0].split("https://www.glassdoor.com/Reviews/")[1].split('-')
        url.pop()
        url.pop()
        url = " ".join(url)
        if check_similarity(name, url) < .5:
            vals = {}
            vals["url"] = info["reviews_url"]
            vals["val"] = check_similarity(name, url)
            output[name] = vals

    print(len(output))
    #with open("problematic.json", "x") as f:
    #    f.write(json.dumps(output, sort_keys=True, indent=2))

def load(name):
    file_path = "{}".format(name)
    if not os.path.exists(file_path):
        return {}
    with open(file_path) as f:
        return json.load(f)

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def main3():
    r1 = load("/Users/duncanross/Desktop/company_reviews_mac1.json")
    r2 = load("/Users/duncanross/Desktop/company_reviews_pc.json")
    r3 = load("/Users/duncanross/Desktop/company_reviews_mac2.json")
    probs = load("data/problematic.json")

    for i, (name, info) in enumerate(probs.items()):
        if name in r1:
            r1.pop(name)
        if name in r2:
            r2.pop(name)
        if name in r3:
            r3.pop(name)
    
    combined = Merge(r1,r2)
    combined = Merge(combined,r3)
    with open("combined_reviews_master.json", "x") as f:
        f.write(json.dumps(combined, sort_keys=True, indent=2))

def main():
    r1 = load("data/company_reviews.json")
    progress = {}
    for i, (name, info) in enumerate(r1.items()):
        progress[name] = 'True'

    with open("data/progress.json", "x") as f:
        f.write(json.dumps(progress, sort_keys=True, indent=2))

def main4():
    names = load("data/company_names.json")
    map = load("data/companies_map_full_list.json")
    data = load("combined_reviews_master.json")
    probs = load("data/problematic.json")
    #r1 = load("/Users/duncanross/Desktop/company_reviews_mac1.json")
    #r2 = load("/Users/duncanross/Desktop/company_reviews_pc.json")
    #r3 = load("/Users/duncanross/Desktop/company_reviews_mac2.json")

    print(len(names))
    print(len(map))
    print(len(data))
    tot = 0

    for c in data:
        tot  += len(data[c])
    
    print(tot)
    print(len(probs))

    missing = []

    for c in map:
        if c not in data:
            missing.append(c)

    with open("data/missingggggg.json", "x") as f:
        f.write(json.dumps(missing, sort_keys=True, indent=2))
    
def mergeLarge():
    r1 = load("data/company_reviews_amazoncom_1.json")
    tot = len(r1["amazoncom"])
    for i in range(2,81):
        r2 = load("data/company_reviews_amazoncom_{}.json".format(i))
        r1["amazoncom"] += r2["amazoncom"]
        tot += len(r2["amazoncom"])

    print(tot)
    with open("last_missing_reviews_AMAZON.json", "x") as f:
        f.write(json.dumps(r1, sort_keys=True, indent=2))

def main5():
    r1 = load("combined_reviews_master.json")
    r2 = load("/Users/duncanross/Desktop/Glassdoor-Research/data/LAST_MISSING_LETS GO.json")
    combined = Merge(r1,r2)
    with open("glassdoor_reviews_final.json", "x") as f:
        f.write(json.dumps(combined, sort_keys=True, indent=2))
    