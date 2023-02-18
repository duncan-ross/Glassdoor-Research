import json
import re
from pprint import pprint
from definitions import *
import code
from pandas.io.json import json_normalize
import pandas as pd
import xlrd
import datetime
import db_helper
import pickle
import json2xlsx
import tablib


# Converts the json produced in company_reviews to a list of dictionaries
def write_revs_to_text():

    # Get the json of company reviews
    with open(COMPANY_REVIEWS) as f:
        data = json.load(f)

    # Get each company that is in the json file
    companies = data.keys()

    # Iterate over each company
    for name in companies:

        code.interact(local=locals())

        # Iterate over each review
        if data.get(name):

            tab_data = tablib.Dataset()
            for rev in data.get(name):

                # Flatten the review
                flat_review = flatten_json(rev)

                # Get the data from the review
                temp = {}
                for key in REVIEW_KEYS:
                    if key == "years_employed":
                        temp[key] = employment_years_to_num(flat_review.get(key))
                    else:
                        temp[key] = flat_review.get(key)

                tab_data.headers = temp.keys()
                tab_data.append(temp.values())

        with open(DATA_DIR + "/" + name + ".txt", "wb") as f:
            f.write(tab_data.tsv)

    return


# Flatten JSON to get only the final key in nested dictionaries
def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


with open(COMPANY_REVIEWS) as f:
    data = json.load(f)

# Converts the text provided of the number of years employed to a number
def employment_years_to_num(em_years):

    # Find if the number of years is greater than or less than
    if em_years is None:
        return None
    elif re.search(">", em_years):
        return float(re.findall("\d+", em_years)[0]) + 0.5
    elif re.search("<", em_years):
        return float(re.findall("\d+", em_years)[0]) - 0.5
    else:
        return None


# For each company, write the company name as a row
# For each review within the company, write the review
write_revs_to_text()
