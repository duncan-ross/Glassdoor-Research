import sys
from fix_company_names import fix_company_names, remove_extraneous, remove_punctuation
import helpers as helpers
import pandas
import json


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

    
"""
Rewrites the companies_map.json file with the ipo dates added and p-values for a company to ipodate match.
"""
def add_ipo_dates():
    # from ipos excel file
    iposexcel_data_df = pandas.read_excel("data/ipo-2000s.xlsx", sheet_name="Sheet1", index_col = None)
    iposexcel_data_df = iposexcel_data_df[['Issuer', 'Date']].drop_duplicates(subset='Issuer', keep="first")
    iposexcel_data_df['Issuer'] = fix_company_names(iposexcel_data_df['Issuer'].tolist())
    iposexcel_data_df = iposexcel_data_df[iposexcel_data_df['Date'].notna()]
    
    # from compustat excel file
    compustat_data_df = pandas.read_excel('data/compustat_data.xlsx', sheet_name='companies', index_col = None)
    compustat_data_df = compustat_data_df[['conm', 'ipodate']].drop_duplicates(subset='conm', keep="first")
    compustat_data_df['conm'] = fix_company_names(compustat_data_df['conm'].tolist())
    compustat_data_df = compustat_data_df[compustat_data_df['ipodate'].notna()]

    companies_map = helpers.json_data('companies_map')
    

    for company in companies_map:
        c = remove_extraneous(remove_punctuation(company).lower().strip())

        # Perfect matches
        if c in iposexcel_data_df['Issuer'].values and not pandas.isnull(iposexcel_data_df[iposexcel_data_df['Issuer'] == c]['Date'].values[0]):
            date , pval , match = iposexcel_data_df[iposexcel_data_df['Issuer'] == c]['Date'].values[0], 1, company
        elif c in compustat_data_df['conm'].values and not pandas.isnull(compustat_data_df[compustat_data_df['conm'] == c]['ipodate'].values[0]):
            date , pval , match = compustat_data_df[compustat_data_df['conm'] == c]['ipodate'].values[0], 1, company
        else:
            # Partial matches
            max_similarity_name_iposecel, max_similarity_iposecel = check_fuzzy_matches(c, iposexcel_data_df['Issuer'].values)
            max_similarity_name_compustat, max_similarity_compustat = check_fuzzy_matches(c, compustat_data_df['conm'].values)
            if max_similarity_iposecel > max_similarity_compustat:
                date, pval, match = iposexcel_data_df[iposexcel_data_df['Issuer'] == max_similarity_name_iposecel]['Date'].values[0], max_similarity_iposecel, max_similarity_name_iposecel
            else:
                date, pval, match = compustat_data_df[compustat_data_df['conm'] == max_similarity_name_compustat]['ipodate'].values[0], max_similarity_compustat, max_similarity_name_compustat
            
            if pval < 0.7:
                date, pval, match = None, 0, None

        companies_map[company]['date'] = date
        companies_map[company]['pval'] = pval
        companies_map[company]['match'] = match

    with open("data/companies_map_new.json", "w") as outfile:
        print("Rewriting companies_map.json")
        json.dump(companies_map, outfile, indent=2, sort_keys=True, default=str)

if __name__ == "__main__":
    add_ipo_dates()