import os
from definitions import DATA_DIR, EXTRANEOUS_WORDS
import string
import json
import pandas
import helpers as helpers

def fetch_company_list(filename,sheet):
    excel_data_df = pandas.read_excel(filename, sheet_name=sheet, index_col = None)
    company_list = excel_data_df['conm'].drop_duplicates().tolist()
    with open("data/company_names.json", "w") as outfile:
        outfile.write(json.dumps(company_list))

# This function checks for any company_names.json, company_map.json, companies_not_found.json, and company_reviews.json and updates the company names to be lower case, trimmed, and removes any punctuation.
def fix_scraped_files(wd):
    files = os.listdir(wd)
    #if "company_names.json" in files:
    #    file = wd + "/company_names.json"
    #    fix_company_names(file)
    if "companies_not_found.json" in files:
        file = wd + "/companies_not_found.json"
        fix_company_names(file)
    #if "companies_map.json" in files:
    #    file = wd + "/companies_map.json"
    #    fix_companies_map(file)
    #if "company_reviews.json" in files:
    #    file = wd + "/company_reviews.json"
    #    fix_companies_map(file)

def fix_company_names(old_company_names):
    new_company_names = [
        remove_extraneous(remove_punctuation(n).lower().strip()) for n in old_company_names
    ]
    return new_company_names

def fix_company_names_in_map(file_name):

    # Open the old file
    with open(file_name) as f:
        old_company_names = json.load(f)

    # Iterate over the company names and apply the transformation
    new_company_names = fix_company_names(old_company_names)

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

def remove_extraneous(str):
    edit_string_as_list = str.split()
    final_list = [word for word in edit_string_as_list if word not in EXTRANEOUS_WORDS]
    return ' '.join(final_list)


def add_ipo_dates():
    # from ipos excel file
    iposexcel_data_df = pandas.read_excel("data/ipo-2000s.xlsx", sheet_name="Sheet1", index_col = None)
    iposexcel_data_df = iposexcel_data_df[['Issuer', 'Date']].drop_duplicates(subset='Issuer', keep="first")
    iposexcel_data_df['Issuer'] = fix_company_names(iposexcel_data_df['Issuer'].tolist())
    
    # from compustat excel file
    compustat_data_df = pandas.read_excel('data/compustat_data.xlsx', sheet_name='companies', index_col = None)
    compustat_data_df = compustat_data_df[['conm', 'ipodate']].drop_duplicates(subset='conm', keep="first")
    compustat_data_df['conm'] = fix_company_names(compustat_data_df['conm'].tolist())

    companies_map = helpers.json_data('companies_map')
    
    for company in companies_map:
        c = remove_extraneous(remove_punctuation(company).lower().strip())
        if c in iposexcel_data_df['Issuer'].values:
            date = iposexcel_data_df[iposexcel_data_df['Issuer'] == c]['Date'].values[0]
        elif c in compustat_data_df['conm'].values:
            date = compustat_data_df[compustat_data_df['conm'] == c]['ipodate'].values[0]
        else:
            date = None
        companies_map[company]['date'] = date

    with open("data/companies_map_new.json", "w") as outfile:
        print("Rewriting companies_map.json")
        json.dump(companies_map, outfile, indent=2, sort_keys=True, default=str)

#fetch_company_list('data/compustat_data.xlsx','companies')
#fix_scraped_files(DATA_DIR)

add_ipo_dates()