from random import uniform
import time
from definitions import GLASSDOOR_REVIEWS_BASE_URL, DATA_DIR, EMPLOYEE_STATUS_FILTER
from helpers import slugify, json_data
from src.api import get_company
import json
from time import sleep

# This function updates companies_map.json using data from company_names.json and companies_not_found.json. It uses the Glassdoor API to retrieve the url of any companies that are in company_names.json, but have not yet been added to companies_map.json or companies_not_found.json.
def updateCompaniesMap():
    company_names = json_data("company_names_2") or []
    companies_map = json_data("companies_map")
    not_found = json_data("companies_not_found") or {}

    print(companies_map)
    print(company_names)
    starting_company_num = len(companies_map)

    # Get the new companies for which reviews will be retrieved
    new_companies = [
        n for n in company_names if n not in companies_map
    ]  # .get(n) and not not_found.get(n)]
    #new_companies += [n for n in not_found]

    not_found = []
    print(new_companies)
    if not new_companies:
        print("No new companies to fetch!")
        return False

    print("Fetching {} companies from Glassdoor...".format(len(new_companies)))

    try:
        for name in new_companies:

            # name = filter(lambda x: x in set(string.printable), name)
            print("Company name: {}".format(name))
            time.sleep(uniform(3,7))
            # Use the Glassdoor API to search for the company's respective URL
            company = get_company(name)
            

            if not company:
                not_found.append(name)
                print("Failure")
                continue
            print("Success")

            companies_map[name] = {
                "reviews_url": reviews_url_for_company(company) + EMPLOYEE_STATUS_FILTER
            }

        print(
            "Found data for {} companies.".format(len(companies_map) - starting_company_num)
        )

        # Add the new company URL's to companies_map.json in real time
        write_results_to_disk(
            {"companies_map_2": companies_map, "companies_not_found_2": not_found}
        )
    except KeyboardInterrupt:
        write_results_to_disk(
            {"companies_map_2": companies_map, "companies_not_found_2": not_found}
        )

    return True


# Creates the URL for the company reviews based on the company URL returned by the Glassdoor API
def reviews_url_for_company(company):
    clean_company_name = slugify(company["name"])
    return "{}/{}-Reviews-E{}.htm".format(
        GLASSDOOR_REVIEWS_BASE_URL, clean_company_name, company["id"]
    )


# Helper function to write results of updateCompaniesMap() to their respective files
def write_results_to_disk(results):
    for filename, data in results.items():
        with open("{}/{}.json".format(DATA_DIR, filename), "w+") as f:
            f.write(json.dumps(data, sort_keys=True, indent=2))


if __name__ == "__main__":
    updateCompaniesMap()
