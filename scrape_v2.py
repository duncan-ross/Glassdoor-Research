from random import *
from definitions import DATA_DIR, DEFAULT_HEADERS, DEFAULT_BATCH_SIZE, USER_AGENT_LIST
from bs4 import BeautifulSoup
import grequests
import requests
import json
import re
import sys
import time
import math
from helpers import json_data, setall, Merge
from get_review_urls import updateCompaniesMap
from dateutil.parser import parse
from legacy_scrape import scrape_review_info_legacy
globaliter = 2
ITERSIZE = 100

# Check if there are any new companies in the companies map to be scraped
def main(fetchAllCompanies=True):

    # Update the companies map with any new companies that the reviews are to be fetched for, and retrieve the companies_map
    #updateCompaniesMap()
    companies_map = json_data("last_missing")
    existing_company_reviews = json_data("company_reviews")
    problems = json_data("problematic1")
    progress = json_data("progress1")
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
        if(name in existing_company_reviews or name in problems or name in progress):
            #if (len(existing_company_reviews[name])>0 or existing_company_reviews[name]):
                #if(len(existing_company_reviews[name])==10):
                #    print("redoing a 10er")
                #else:
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
        if num_pages > 1000:
            continue

        responses = get_review_pages(reviewsUrl, num_pages)
        # Iterate responses and parse data
        companyReviews = []
        for index, response in responses.items():
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

def mainForCompany(name, URL):

    # Update the companies map with any new companies that the reviews are to be fetched for, and retrieve the companies_map
    #updateCompaniesMap()

    # Either force all reviews to be refetched, or find which companies' reviews haven't been retrieved yet
    reviewsUrl = URL
    num_pages = get_num_pages(reviewsUrl)
    print("Num pages : %s" % num_pages)
    reviewsData = {}
    # Fetch all reviews
    start = time.time()

    responses = get_review_pages(reviewsUrl, ITERSIZE)
    # Iterate responses and parse data
    companyReviews = []
    for index, response in responses.items():
        page_data = fetch_review_page_data(index, response)
        if page_data:
            companyReviews += page_data

    reviewsData[name] = companyReviews
    write_reviews_to_file_company(name, reviewsData,globaliter)
    print(
        "Found {} review(s) for {} in {:.3f} seconds".format(
            len(companyReviews), name, time.time() - start
        )
    )


def get_review_pages(reviewsUrl, num_pages):
    responses = {}
    setall(responses, range(1, num_pages+1), None)
    done = False

    for j in range(max(math.floor(num_pages/250), 5)):
        if (done): 
            break
        print("Attempting pass #{} of batches".format(j+1))
        responses, done = get_batched_requests(reviewsUrl, responses)
        time.sleep(uniform(10,15))
    
    if not done:
        for i, r in responses.items():
            if not check_response(r):
                r = get_single_request(reviewsUrl, i)

    return responses



def get_batched_requests(reviewsUrl, responses):
    pages, new_responses = [], {}
    done = True
    for i, r in responses.items():
        if not r:
            pages.append(i)
        if len(pages) == DEFAULT_BATCH_SIZE:
            rs = generate_url_map(reviewsUrl, pages)
            new_responses = Merge(new_responses, dict(zip(pages, grequests.map(rs))))
            print("Progress: {}/{}".format(len(new_responses),len(responses)))
            pages = []
            time.sleep(uniform(10,12))
        

    if len(pages) > 0:
        rs = generate_url_map(reviewsUrl, pages)
        new_responses = Merge(new_responses, dict(zip(pages, grequests.map(rs))))
        print("Progress: {}/{}".format(len(new_responses),len(responses)))

    for i, r in new_responses.items():
        responses[i] = new_responses[i]
        if not check_response(r):
            responses[i] = None
            done = False
    
    return responses, done



def generate_url_map(reviewsUrl, pages):
    rs = (
        grequests.get(
            reviewsUrl.replace(".htm", "_P" + str(p+(globaliter-1)*ITERSIZE) + ".htm"),
            headers={"User-Agent": choice(USER_AGENT_LIST)}
        )
        for p in pages
        )
    return rs



def retry_batches(reviewsUrl, retry_batch):
    print("Retrying {} requests.".format(len(retry_batch)))
    batch = 100
    responses = []
    for j in range(math.ceil(len(retry_batch)/batch)):
        time.sleep(uniform(5,7))
        print("Retrying-- Batching requests: {}/{}".format(min(len(retry_batch), (j+1)*batch),len(retry_batch)))
        rs = (
            grequests.get(
                reviewsUrl.replace(".htm", "_P" + str(list(retry_batch.keys())[k] + 1) + ".htm"),
                headers={"User-Agent": choice(USER_AGENT_LIST)}
            )
            for k in range(min(len(retry_batch), (j)*batch), min(len(retry_batch), (j+1)*batch))
        )
        responses += grequests.map(rs)
    
    x = {}
    for i in range(len(retry_batch)):
        x[list(retry_batch.keys())[i]] = responses[i]
    return x


# Checks if a given GET response has the information we need.
def check_response(response):
    if not response or not response.content or response.status_code != 200:
        return False
    else:
        soup = BeautifulSoup(response.content, "html.parser")
        if not soup or not soup.find_all(attrs={"class": "emp-reviews-feed"}):
            return False
    
    return True


# Retry getting the page data for failed responses
def get_single_request(reviewsUrl, page_num):
    print("Retrying page {}".format(page_num))
    for _ in range(5):
        time.sleep(uniform(1,3))
        try:
            response = requests.get(
                        reviewsUrl.replace(".htm", "_P" + str(page_num + 1) + ".htm"),
                        headers=DEFAULT_HEADERS,
                    )
            if(response and response.content):
                print("Success")
                return response
        except Exception as e:
            print("exception")
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

    reviews_feed = soup.find_all(attrs={"class": "emp-reviews-feed"})

    reviews_soup = reviews_feed[0].find_all("li", attrs={"class": "empReview"})

    reviews_data = re.search(r'"reviews":(\[.*?}\])}', response.text, flags=re.S)

    data = []
    if reviews_data:
        reviews_data = reviews_data.group(1)
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
    else:
        return data
    
    for review_soup, review_data in zip(reviews_soup, reviews_data):
        try:
            review_info = scrape_review_info(review_soup, review_data)
        except Exception:
            review_info = None

        if review_info:
            data.append(review_info)

    return data


# Scrape the review info from the html from a single review
def scrape_review_info(soup, data):
    review = {}
    if not data:
        return None

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
    if "pros" in data:
        review["pros"] = data["pros"]
    else:
        review["pros"] = None

    if "cons" in data:
        review["cons"] = data["cons"]
    else:
        review["cons"] = None

    if "advice" in data:
        review["advice"] = data["advice"]
    else:
        review["advice"] = None
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

# Writes the reviews to company_reviews.json in real time
def write_reviews_to_file_company(name, reviewsData, iter):
    with open("{}/company_reviews_{}_{}.json".format(DATA_DIR,name,iter), "w+") as f:
        f.write(json.dumps(reviewsData, sort_keys=True, indent=2))


if __name__ == "__main__":
    force = "--force" in sys.argv
    # main(fetchAllCompanies=force)
    #main()

    while globaliter < 148:
        mainForCompany("amazoncom","https://www.glassdoor.com/Reviews/Amazon-Reviews-E6036.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.employmentStatus=FREELANCE&filter.employmentStatus=PART_TIME&filter.employmentStatus=CONTRACT&filter.employmentStatus=INTERN&filter.employmentStatus=REGULAR")
        globaliter +=1