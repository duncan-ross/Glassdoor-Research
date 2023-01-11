from definitions import DATA_DIR, DEFAULT_HEADERS, RATING_LABELS_DICT, STAR_COUNT_DICT
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

# Check if there are any new companies in the companies map to be scraped
def main(fetchAllCompanies=False):

    # Update the companies map with any new companies that the reviews are to be fetched for, and retrieve the companies_map
    updateCompaniesMap()
    companies_map = json_data("companies_map")
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

    # Fetch all reveiws (company_names currently contains 01/02/10-05/31/17)
    for i, (name, info) in enumerate(new_companies_map.items()):
        start = time.time()
        print(
            "{}/{}: Finding reviews for {}".format(i + 1, len(new_companies_map), name)
        )
        reviewsUrl = info["reviews_url"]

        num_pages = get_num_pages(reviewsUrl)
        print("num pages = %s" % num_pages)

        # Break condition for too many reviews
        if num_pages > 1000:
            print("Number of pages >1000, skipping for now...")
            continue

        companyReviews = []

        rs = (
            grequests.get(
                reviewsUrl.replace(".htm", "_P" + str(j + 1) + ".htm"),
                headers=DEFAULT_HEADERS,
            )
            for j in range(num_pages)
        )
        responses = grequests.map(rs)

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


# Returns the beautiful soup html content for a given url
def get_html_body(url):
    sauce = requests.get(url, headers=DEFAULT_HEADERS)
    soup = BeautifulSoup(sauce.content, "html.parser")
    return soup


# Gets the number of pages of reviews per company by finding the total number of reviews and then dividing by number of reviews per page (10)
def get_num_pages(url):
    body = get_html_body(url)
    numReviewsString = body.find("div", {"class": "paginationFooter"}).text
    res = max([int(i) for i in numReviewsString.split() if i.isdigit()])
    return math.ceil(res / 10)


# Get the html from a page of reviews (e.g. page 3 of the reviews for Secure Works)
def fetch_review_page_data(page_num, response):
    print("Page " + str(page_num))

    body = BeautifulSoup(response.content, "html.parser")

    appData = re.search(r'"reviews":(\[.*?}\])}', response.text, flags=re.S).group(1)
    if appData:
        appData = json.loads(appData)

    if not body:
        return False

    reviews_feed = body.find_all(attrs={"class": "emp-reviews-feed"})

    if not reviews_feed:
        return False

    reviews = reviews_feed[0].find_all("li", attrs={"class": "empReview"})

    data = []
    for index, review in enumerate(reviews):
        review_info = scrape_review_info_legacy(review)
        if appData[index]["advice"]:
            review_info["advice_to_mgmt"] = appData[index]["advice"]

        if review_info:
            data.append(review_info)

    return data


# Scrape the review info from the html from a single review
def scrape_review_info_legacy(body):
    review = {}

    # Get the text information
    parse_text_information(body, review)

    # Get the overall star rating
    parse_star_rating(body, review)

    # Get the date the review was posted
    parse_date_role_location(body, review)

    # Get the employment status and tenure of the reviewer
    parse_current_employment_status_tenure(body, review)

    get_approval_info(body, review)

    return review


# Find the main text information such as pros, cons, advice to management
def parse_text_information(soup, review):
    for field, info in class_details_map().items():
        tag = info["tag"]
        class_type = info["class_type"]
        class_names = info["class_name"]

        if len(class_names) > 1:
            text_el, i = None, 0
            while text_el is None and i < len(class_names):
                text_el = soup.find(tag, attrs={class_type: class_names[i]})
                i = i + 1

        else:
            text_el = soup.find(tag, attrs={class_type: class_names[0]})

        if text_el:
            review[field] = text_el.text
        else:
            review[field] = None
    review["advice_to_mgmt"] = None
    return


# Finds and retunrs the overall star rating of the company as well as the breakdown in star rating between culture & values, work/life balance, senior management, comp & benefits, and career opportunities
def parse_star_rating(soup, review):
    overallRating = soup.find("span", attrs={"class": "ratingNumber"}).text

    if not overallRating:
        return None

    review["overall_rating"] = float(overallRating)

    subRatingMenu = soup.find("aside", attrs={"class": "gd-ui-tooltip-info"})
    missing_sub_star_ratings(review)

    if subRatingMenu:
        parse_sub_star_ratings(subRatingMenu, review)

    return


# Given subratings menu, adds secondary ratings to review
def parse_sub_star_ratings(soup, review):
    ratings = soup.findAll("li")

    for r in ratings:
        text = " ".join([el.text for el in r.findAll("div", text=True)])
        for k, v in RATING_LABELS_DICT.items():
            if k in text.lower():
                review[v] = parse_star_val(review, r)
                break
    return


# Marks all sub ratings as null
def missing_sub_star_ratings(review):
    for r in RATING_LABELS_DICT.values():
        review[r] = None

    return


# Returns the value of the 'title' class within an element
def parse_star_val(review, rating):
    for k, v in STAR_COUNT_DICT.items():
        if rating.find("div", attrs={"class": k}):
            return v

    print(rating)
    print(review)
    raise Exception("SubMenu Ratings not found properly: ")


# Finds and returns the date that a review was posted
def parse_date_role_location(soup, review):
    jobLine_el = soup.find(
        "span", attrs={"class": "common__EiReviewDetailsStyle__newUiJobLine"}
    )
    jobLine_arr = [
        s.strip()
        for s in jobLine_el.find(
            "span", attrs={"class": "common__EiReviewDetailsStyle__newGrey"}
        ).text.split("-")
    ]
    date, role = jobLine_arr[0], jobLine_arr[1]
    date = parse(date).strftime("%m/%d/%Y")

    try:
        location = (
            (jobLine_el.findAll("span", attrs={"class": "middle"})[1]).find("span").text
        )
    except (IndexError):
        location = None
        pass

    review["date"] = date if date else None
    review["job_title"] = role if role else None
    review["location"] = location if location else None
    return


# Finds and returns the job title and status of the employee posting a review
def parse_current_employment_status_tenure(soup, review):
    jobStatusTenure = soup.find(
        "span", attrs={"class": "pt-xsm pt-md-0 css-1qxtz39 eg4psks0"}
    ).text
    current_employee = "current" in jobStatusTenure.lower()

    employment_types = ["full-time", "part-time", "contract", "intern", "freelance"]
    employment_status = None

    for employment_type in employment_types:
        if re.search(
            r"\b" + re.escape(employment_type) + r"\b", jobStatusTenure.lower()
        ) or re.search(r"\b" + re.escape(employment_type) + r"\b", review["job_title"]):
            employment_status = employment_type

    try:
        tenure_text = jobStatusTenure.lower().split(",")[1]
        years = str(max([int(i) for i in tenure_text.split() if i.isdigit()]))
        if "less" in tenure_text:
            tenure = "<" + years
        elif "more" in tenure_text:
            tenure = ">" + years
        else:
            tenure = years
    except (IndexError):
        tenure = None

    review["current_employee"] = current_employee
    review["years_employed"] = tenure
    review["employment_status"] = employment_status
    return


# Finds and returns the approval info in three categories: recommend to a friend, approves of CEO, and company outlook
def get_approval_info(soup, review):
    categories = ["recommends", "approves_of_ceo", "business_outlook"]

    reccomendations = soup.find("div", attrs={"class": "reviewBodyCell"}).findAll(
        "div", attrs={"class": "d-flex align-items-center mr-std"}
    )

    for i, r in enumerate(reccomendations):
        if len(r.findAll("span", attrs={"class": "css-hcqxoa"})) > 0:
            review[categories[i]] = "positive"
        elif len(r.findAll("span", attrs={"class": "css-1kiw93k"})) > 0:
            review[categories[i]] = "negative"
        elif len(r.findAll("span", attrs={"class": "css-1h93d4v"})) > 0:
            review[categories[i]] = "neutral"
        elif len(r.findAll("span", attrs={"class": "css-10xv9lv"})) > 0:
            review[categories[i]] = "unspecified"
        else:
            review[categories[i]] = "ERROR"

    return


# Helper function to get_approval_info()
def category_for_text(text):
    category_match_map = {
        "recommend": "recommends",
        "outlook": "outlook",
        "ceo": "approves_of_ceo",
    }

    for p, k in category_match_map.items():
        if re.search(p, text, re.I):
            return k

    return None


# Creates a map containing information on classes where the information wanted is text within the given element
def class_details_map():
    return {
        "review_summary": {
            "tag": "h2",
            "class_type": "class",
            "class_name": ["reviewLink", "mb-xxsm mt-0 css-93svrw el6ke055"],
        },
        "pros": {"tag": "span", "class_type": "data-test", "class_name": ["pros"]},
        "cons": {"tag": "span", "class_type": "data-test", "class_name": ["cons"]},
    }


# Writes the reviews to company_reviews.json in real time
def write_reviews_to_file(reviewsData):
    with open("{}/company_reviews.json".format(DATA_DIR), "w+") as f:
        f.write(json.dumps(reviewsData, sort_keys=True, indent=2))


if __name__ == "__main__":
    force = "--force" in sys.argv
    # main(fetchAllCompanies=force)
    main(fetchAllCompanies=True)
