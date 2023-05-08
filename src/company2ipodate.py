import sys
from fix_company_names import fix_company_names, remove_extraneous, remove_punctuation
import helpers as helpers
import pandas
import json
from helpers import slugify


"""
Given a company name and a list of company names, this function returns the closest match using the helpers.check_similarity function.
"""
def check_fuzzy_matches(name, company_list):
    max_similarity = 0
    max_similarity_name = ""
    for company in company_list:
        similarity = helpers.check_similarity(name, company)
        if similarity > max_similarity:
            max_similarity = similarity
            max_similarity_name = company
    
    return max_similarity_name, max_similarity

"""Given a compustat df and company name, this function returns the ipodate, ticker and cusip of the company."""
def retrieve_compustat_info(df, company):
    row = df[df['conm1'] == company]
    if row.empty:
        row = df[df['conm2'] == company]
    if row.empty:
        return None, None, None
    
    ipodate = row['ipodate'].values[0] if not pandas.isnull(row['ipodate'].values[0]) else None
    ticker = row['tic'].values[0] if not pandas.isnull(row['tic'].values[0]) else None
    cusip = row['cusip'].values[0] if not pandas.isnull(row['cusip'].values[0]) else None
    return ipodate, ticker, cusip


def add_ipo_dates():
    # from ipos excel file
    iposexcel_data_df = pandas.read_excel("data/IPO-age_ufl.xlsx", sheet_name="Sheet1", index_col = None)
    iposexcel_data_df = iposexcel_data_df[["IPO_name", "Offer_date", "Ticker", "CUSIP"]]

    compustat_data_df = pandas.read_excel('data/compustat_data.xlsx', sheet_name='companies', index_col = None)
    compustat_data_df = compustat_data_df[['conm', 'ipodate', 'tic', 'cusip']]
    compustat_data_df['conm2'] = [remove_extraneous(remove_punctuation(c).lower().strip()).lower() for c in compustat_data_df['conm'].tolist()]
    compustat_data_df['conm1'] = [slugify(c).lower() for c in compustat_data_df['conm'].tolist()]
    
    companies_map = helpers.json_data('companies_map')


    counter = 0
    for c in companies_map:
        ipo_date, ticker, cusip = retrieve_compustat_info(compustat_data_df, c)
        if ipo_date is None and ticker is None and cusip is None:
            ipo_date, ticker, cusip = retrieve_compustat_info(compustat_data_df, slugify(c).lower())
        if ipo_date is None and ticker is None and cusip is None:
            ipo_date, ticker, cusip = retrieve_compustat_info(compustat_data_df, remove_extraneous(remove_punctuation(c).lower().strip()))
        
        if ipo_date is not None:
            counter += 1
            companies_map[c]['date'] = ipo_date
            companies_map[c]['ticker'] = ticker
            companies_map[c]['cusip'] = cusip
            continue
        
        # match ticker to ipo date using the iposexcel file
        # check that ipo date is not null
        if ticker in iposexcel_data_df['Ticker'].values:
            ipo_date = iposexcel_data_df[iposexcel_data_df['Ticker'] == ticker]['Offer_date'].values[0]
            if ipo_date == "NaT":
                print('here')
            companies_map[c]['date'] = ipo_date
            companies_map[c]['ticker'] = ticker
            companies_map[c]['cusip'] = cusip
            continue

        # match cusip to ipo date using the iposexcel file
        if cusip in iposexcel_data_df['CUSIP'].values:
            ipo_date = iposexcel_data_df[iposexcel_data_df['CUSIP'] == cusip]['Offer_date'].values[0]
            companies_map[c]['date'] = ipo_date
            companies_map[c]['ticker'] = ticker
            companies_map[c]['cusip'] = cusip
            continue



        companies_map[c]['date'] = None
        companies_map[c]['ticker'] = None
        companies_map[c]['cusip'] = None

    print(f"Found {counter} ticker matches")
    misses = len([c for c in companies_map if not companies_map[c]['date']])
    print(f"Misses: {misses} out of {len(companies_map)}")
    with open("data/companies_map_new.json", "w") as outfile:
        print("Rewriting companies_map.json")
        json.dump(companies_map, outfile, indent=2, sort_keys=True, default=str)

"""
Turns the companies_map_new.json file into a csv file.
The json is of format:
{
    "company_name": {
        "date": "ipo date",
        "ticker": "ticker",
        "cusip": "cusip",
        "reviews_url": "url to reviews"
    }
}

The csv is of format:
index, company_name, date, ticker, cusip, reviews_url
"""
def json_to_csv():
    companies_map = helpers.json_data('companies_map_new')
    with open("data/companies_map_new.csv", "w") as outfile:
        outfile.write("index,company_name,date,ticker,cusip,reviews_url\n")
        for i, c in enumerate(companies_map):
            outfile.write(f"{i},{c},{companies_map[c]['date']},{companies_map[c]['ticker']},{companies_map[c]['cusip']},{companies_map[c]['reviews_url']}\n")

if __name__ == "__main__":
    add_ipo_dates()
    json_to_csv()