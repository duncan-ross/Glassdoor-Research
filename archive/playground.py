import json
from math import ceil
import requests
from urllib.request import Request, urlopen
import bs4 as bs
import re

from helpers import json_data

LOCAL_IP = "192.168.0.50"
GLASSDOOR_API_HOST_URL = "http://api.glassdoor.com/api/api.htm"
GLASSDOOR_PARTNER_ID = "157426"
GLASSDOOR_PARTNER_KEY = "iDIHGVDrCcA"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}


def base_payload(action, query):
    return {
        "v": "1",
        "format": "json",
        "t.p": GLASSDOOR_PARTNER_ID,
        "t.k": GLASSDOOR_PARTNER_KEY,
        "userip": LOCAL_IP,
        "country": "us",
        "action": action,
        "q": query,
    }


payload = base_payload("employers", "Google")
# r = requests.get(GLASSDOOR_API_HOST_URL, params=payload, headers=DEFAULT_HEADERS)

# json_response = r.json()
# response = json_response.get('response')
# print(response)

url = "https://www.glassdoor.com/Reviews/Alteryx-Reviews-E351220.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.employmentStatus=FREELANCE&filter.employmentStatus=PART_TIME&filter.employmentStatus=CONTRACT&filter.employmentStatus=INTERN&filter.employmentStatus=REGULAR"
# req = Request(url, headers=DEFAULT_HEADERS)
# mybytes = urlopen(req).read()
# mystr = mybytes.decode("utf8")
# print(mystr)

sauce = requests.get(url, headers=DEFAULT_HEADERS)
soup = bs.BeautifulSoup(sauce.content, "html.parser")
# site_json=json.loads(soup.text)

print(str(soup))

# print(sauce.content)
with open("data/testing.txt", "w") as outfile:
    outfile.write(str(soup))

numReviewsString = soup.find("div", {"class": "paginationFooter"}).text
# print(numReviewsString)
result = numReviewsString[numReviewsString.find("of") :]
res = max([int(i) for i in numReviewsString.split() if i.isdigit()])
# print(res)

test_sentence = "international please dont include it intern"
# print("intern" in test_sentence)

# print(bool(re.search(r"\b" + re.escape("intern") + r"\b", test_sentence)))

names_test = json_data("names_test")

names = set()

for n in names_test:
    names.add(n["names:"])

res = list(names)

json_object = json.dumps(res)

# Writing to sample.json
with open("data/sample.json", "w") as outfile:
    outfile.write(json_object)
