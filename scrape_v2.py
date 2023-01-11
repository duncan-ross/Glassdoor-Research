from random import *
from definitions import DATA_DIR, DEFAULT_HEADERS
from bs4 import BeautifulSoup
import grequests
import requests
import json
import re
import sys
import time
import math
from helpers import json_data
from get_review_urls import updateCompaniesMap
from dateutil.parser import parse
from legacy_scrape import scrape_review_info_legacy

# Check if there are any new companies in the companies map to be scraped
def main(fetchAllCompanies=False):

    # Update the companies map with any new companies that the reviews are to be fetched for, and retrieve the companies_map
    #updateCompaniesMap()
    companies_map = json_data("companies_map")
    existing_company_reviews = json_data("company_reviews")
    numReviewsFetched = 0

    # Either force all reviews to be refetched, or find which companies' reviews haven't been retrieved yet
    if fetchAllCompanies:
        reviewsData = {}
        new_companies_map = companies_map
    else:
        print("fetching review data...")
        reviewsData = json_data("company_reviews")
        new_companies_map = {
            k: v for k, v in companies_map.items() if reviewsData.get(k) is None
        }
        print("new_companies_map = %s" % new_companies_map)

    print("Fetching reviews for {} companies".format(len(new_companies_map)))

    reviewsData = existing_company_reviews
    # Fetch all reviews
    for i, (name, info) in enumerate(new_companies_map.items()):
        if(name in existing_company_reviews):
            if (len(existing_company_reviews[name])>0 or existing_company_reviews[name]):
                if(len(existing_company_reviews[name])==10):
                    print("redoing a 10er")
                else:
                    continue
            #if ("DECODER ERROR" in existing_company_reviews[name][0]):
            #    print("Trying to fix: {}".format(name))
            #else:
            #    continue

        time.sleep(uniform(3,7))
        start = time.time()
        print(
            "{}/{}: Finding reviews for {}".format(i + 1, len(new_companies_map), name)
        )
        reviewsUrl = info["reviews_url"]

        num_pages = get_num_pages(reviewsUrl)
        print("Num pages : %s" % num_pages)

        responses = get_batched_requests(reviewsUrl, num_pages)

        # Iterate responses and parse data
        companyReviews = []
        for index, response in enumerate(responses):
            page_data = fetch_review_page_data(index, response)
            if page_data:
                companyReviews += page_data

        reviewsData[name] = companyReviews
        numReviewsFetched += len(companyReviews)
        write_reviews_to_file(reviewsData)
        print(
            "Found {} review(s) for {} in {:.3f} seconds".format(
                len(companyReviews), name, time.time() - start
            )
        )

    print("TOTAL REVIEWS FETCHED: {}".format(numReviewsFetched))


def get_batched_requests(reviewsUrl, num_pages):
    # Send the requests for every page simultaneously
    batch = 100
    responses = []
    for j in range(math.ceil(num_pages/batch)):
        print("Batching requests: {}/{}".format(min(num_pages, (j+1)*batch),num_pages))
        rs = (
            grequests.get(
                reviewsUrl.replace(".htm", "_P" + str(k + 1) + ".htm"),
                headers=DEFAULT_HEADERS,
            )
            for k in range(min(num_pages, (j)*batch), min(num_pages, (j+1)*batch))
        )
        responses += grequests.map(rs)
        time.sleep(uniform(10,15))
    
    for i, response in enumerate(responses):
        if not response or not response.content:
            response = retry_failed_request(reviewsUrl, i)
        else:
            soup = BeautifulSoup(response.content, "html.parser")
            if not soup or not soup.find_all(attrs={"class": "emp-reviews-feed"}):
                response = retry_failed_request(reviewsUrl, i)
    
    return responses


# Retry getting the page data for failed responses
def retry_failed_request(reviewsUrl, page_num):
    print("Retrying page {}".format(page_num))
    for _ in range(5):
        response = requests.get(
                    reviewsUrl.replace(".htm", "_P" + str(page_num + 1) + ".htm"),
                    headers=DEFAULT_HEADERS,
                )
        if(response and response.content):
            print("Success")
            return response
        time.sleep(uniform(1,3))
    print("Failed")
    return None
    

# Returns the beautiful soup html content for a given url
def get_html_body(url):
    sauce = requests.get(url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(sauce.content, "html.parser")
    return soup


# Gets the number of pages of reviews per company by finding the total number of reviews and then dividing by number of reviews per page (10)
def get_num_pages(url):
    body = get_html_body(url)
    numReviewsString = body.find("div", {"class": "paginationFooter"})
    if not numReviewsString:
        return 1
    res = max([int(i) for i in numReviewsString.text.replace(',', '').split() if i.isdigit()])
    return math.ceil(res / 10)


# Get the html from a page of reviews (e.g. page 3 of the reviews for Secure Works)
def fetch_review_page_data(page_num, response):
    print("Parsing page " + str(page_num))
    if not response or not response.content:
        return {"PAGE_FAILURE":page_num}
    soup = BeautifulSoup(response.content, "html.parser")
    #if not soup:
    #    return None

    reviews_feed = soup.find_all(attrs={"class": "emp-reviews-feed"})
    #if not reviews_feed:
    #    return None

    reviews_soup = reviews_feed[0].find_all("li", attrs={"class": "empReview"})

    reviews_data = re.search(r'"reviews":(\[.*?}\])}', response.text, flags=re.S).group(
        1
    )
    data = []
    if reviews_data:
        try:
            reviews_data = json.loads(reviews_data)
        except(json.decoder.JSONDecodeError):
            print("Attempting legacy scrape")
            for review in reviews_soup:
                review_info = scrape_review_info_legacy(review)
                review_info["advice"] = None
                if review_info:
                    data.append(review_info)

            return data
    
    for review_soup, review_data in zip(reviews_soup, reviews_data):
        review_info = scrape_review_info(review_soup, review_data)
        if review_info:
            data.append(review_info)

    return data


# Scrape the review info from the html from a single review
def scrape_review_info(soup, data):
    review = {}

    # Get the text information
    parse_text_information(data, review)

    # Get the star ratings and approvals
    parse_ratings(data, review)

    # Get the review date, employee role and location (if available)
    parse_date_role_location(soup, review)

    # Get the employment status and tenure of the reviewer
    parse_current_employment_status_tenure(soup, data, review)

    return review


# Find the main text information such as pros, cons, advice to management
def parse_text_information(data, review):
    review["pros"] = data["pros"]
    review["cons"] = data["cons"]
    review["advice"] = data["advice"]
    return


# Finds and retunrs the overall star rating of the company as well as the breakdown in star rating between culture & values, work/life balance, senior management, comp & benefits, and career opportunities
def parse_ratings(data, review):
    review["ratingOverall"] = data["ratingOverall"]
    review["ratingCareerOpportunities"] = data["ratingCareerOpportunities"]
    review["ratingCompensationAndBenefits"] = data["ratingCompensationAndBenefits"]
    review["ratingCultureAndValues"] = data["ratingCultureAndValues"]
    review["ratingDiversityAndInclusion"] = data["ratingDiversityAndInclusion"]
    review["ratingSeniorLeadership"] = data["ratingSeniorLeadership"]
    review["ratingWorkLifeBalance"] = data["ratingWorkLifeBalance"]
    review["ratingBusinessOutlook"] = data["ratingBusinessOutlook"]
    review["ratingCeo"] = data["ratingCeo"]
    review["ratingRecommendToFriend"] = data["ratingRecommendToFriend"]
    return


# Finds and returns the date that a review was posted
def parse_date_role_location(soup, review):
    jobLine_el = soup.find(
        "span", attrs={"class": "common__EiReviewDetailsStyle__newUiJobLine"}
    )
    if jobLine_el:
        jobLine_arr = [
            s.strip()
            for s in jobLine_el.find(
                "span", attrs={"class": "common__EiReviewDetailsStyle__newGrey"}
            ).text.split("-")
        ]
    else:
        jobLine_arr = [None, None]
    date, role = jobLine_arr[0], jobLine_arr[1]
    if date:
        date = parse(date).strftime("%m/%d/%Y")

    try:
        location = (
            (jobLine_el.findAll("span", attrs={"class": "middle"})[1]).find("span").text
        )
    except (AttributeError, IndexError):
        location = None
        pass

    review["date"] = date if date else None
    review["job_title"] = role if role else None
    review["location"] = location if location else None
    return


# Finds and returns the job title and status of the employee posting a review
def parse_current_employment_status_tenure(soup, data, review):
    jobStatusTenure = soup.find(
        "span", attrs={"class": "pt-xsm pt-md-0 css-1qxtz39 eg4psks0"}
    )
    try:
        tenure_text = jobStatusTenure.text.lower().split(",")[1]
        years = str(max([int(i) for i in tenure_text.split() if i.isdigit()]))
        if "less" in tenure_text:
            tenure = "<" + years
        elif "more" in tenure_text:
            tenure = ">" + years
        else:
            tenure = years
    except (AttributeError, IndexError):
        tenure = None

    review["current_employee"] = data["isCurrentJob"]
    review["employmentStatus"] = data["employmentStatus"]
    review["years_employed"] = tenure
    return


# Writes the reviews to company_reviews.json in real time
def write_reviews_to_file(reviewsData):
    with open("{}/company_reviews.json".format(DATA_DIR), "w+") as f:
        f.write(json.dumps(reviewsData, sort_keys=True, indent=2))


if __name__ == "__main__":
    force = "--force" in sys.argv
    # main(fetchAllCompanies=force)
    main(fetchAllCompanies=True)
