import os
from definitions import DATA_DIR
import string
import code
import json


# This function checks for any company_names.json, company_map.json, companies_not_found.json, and company_reviews.json and updates the company names to be lower case, trimmed, and removes any punctuation.
def fix_scraped_files(wd):
    files = os.listdir(wd)
    if "company_names.json" in files:
        file = wd + "/company_names.json"
        fix_company_names(file)
    if "companies_not_found.json" in files:
        file = wd + "/companies_not_found.json"
        fix_company_names(file)
    if "companies_map.json" in files:
        file = wd + "/companies_map.json"
        fix_companies_map(file)
    if "company_reviews.json" in files:
        file = wd + "/company_reviews.json"
        fix_companies_map(file)


def fix_company_names(file_name):

    # Open the old file
    with open(file_name) as f:
        old_company_names = json.load(f)

    # Iterate over the company names and apply the transformation
    new_company_names = [
        remove_punctuation(n).lower().strip() for n in old_company_names
    ]

    # Rewrite the company names
    with open(file_name, "w") as outfile:
        print("Rewriting " + file_name)
        json.dump(new_company_names, outfile, indent=2, sort_keys=True)


def fix_companies_map(file_name):
    with open(file_name) as f:
        old_company_map = json.load(f)

    new_company_map = {}
    for k in old_company_map:
        new_company_map[remove_punctuation(k).lower().strip()] = old_company_map[k]

    with open(file_name, "w") as outfile:
        print("Rewriting " + file_name)
        json.dump(new_company_map, outfile, indent=2, sort_keys=True)


def remove_punctuation(str):
    return "".join(c for c in str if c not in string.punctuation)


fix_scraped_files(DATA_DIR + "/rescrape_02_14_19/public_control")
