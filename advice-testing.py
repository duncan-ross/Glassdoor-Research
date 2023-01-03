import json
import pprint
import re
import requests
from urllib.request import Request, urlopen
import bs4 as bs

LOCAL_IP = "192.168.0.50"
GLASSDOOR_API_HOST_URL = "http://api.glassdoor.com/api/api.htm"
GLASSDOOR_PARTNER_ID = "157426"
GLASSDOOR_PARTNER_KEY = "iDIHGVDrCcA"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
url = "https://www.glassdoor.com/Reviews/Alteryx-Reviews-E351220.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.employmentStatus=FREELANCE&filter.employmentStatus=PART_TIME&filter.employmentStatus=CONTRACT&filter.employmentStatus=INTERN&filter.employmentStatus=REGULAR"

html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

reviews = re.search(r'"reviews":(\[.*?}\])}', html, flags=re.S).group(1)
reviews = json.loads(reviews)


titles = re.search(
    r'"jobTitlesByEmployer\(\{\\\"employerId\\\"\:\d*\}\)\"\:(.*?}\])', html, flags=re.S
).group(1)
titles = json.loads(titles)


jobTitles = {}
for t in titles:
    jobTitles[t["jobTitleId"]] = t["jobTitle"]

pprint.pprint(reviews)

# print(jobTitles)
for r in reviews:
    if r["jobTitle"] and r["jobTitle"]["__ref"]:
        num = re.sub("[^\d\.]", "", r["jobTitle"]["__ref"])
        # print(num)
        # print(r['jobTitle'])
        # r['jobTitle'] = jobTitles[num]
