from definitions import DATA_DIR, DEFAULT_HEADERS
from bs4 import BeautifulSoup
import requests
import json
import re
import sys
import time
from math import ceil
from helpers import json_data
from get_review_urls import updateCompaniesMap


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
        print("{}/{}: Finding reviews for {}".format(i+1, len(new_companies_map), name))
        reviewsUrl = info["reviews_url"]

        num_pages = get_num_pages(reviewsUrl)
        print("num pages = %s" % num_pages)

        # Break condition for too many reviews
        if num_pages > 1000:
            print("Number of pages >1000, skipping for now...")
            continue

        companyReviews = []

        for j in range(num_pages):
            page_data = fetch_review_page_data(reviewsUrl, j + 1)
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

# Gets the number of pages of reviews per company by finding the total number of reviews and then dividing by number of reviews per page (10)
def get_num_pages(url):
  sauce = requests.get(url, headers=DEFAULT_HEADERS)
  soup = BeautifulSoup(sauce.content,'html.parser')

  numReviewsString = soup.find("div", {"class": "paginationFooter"}).text
  print(numReviewsString)
  result = numReviewsString[numReviewsString.find("of"):]
  res = max([int(i) for i in numReviewsString.split() if i.isdigit()])
  print(res)








    


# Get the html from a page of reviews (e.g. page 3 of the reviews for Secure Works)
def fetch_review_page_data(url, page_num):
    if page_num > 1:
        # Old code
        #   url = '{}_P{}.htm'.format(url.rstrip('.htm'), page_num)
        # New code that handles adding freelancers, contractors, & interns. Glassdoor started auto-filtering for just full-time and part-time employees
        url = url.replace(".htm", "_P" + str(page_num) + ".htm")
        print("Page " + str(page_num))

    body = get_html_body(url)

    if not body:
        return []

    reviews_feed = body.find_all(attrs={"class": "emp-reviews-feed"})

    if not reviews_feed:
        return

    reviews = reviews_feed[0].find_all("li", attrs={"class": "empReview"})

    data = []
    for el in reviews:
        review_info = scrape_review_info(el)

        if review_info:
            data.append(review_info)

    return data


# Scrape the review info from the html from a single review
def scrape_review_info(el):
    review = {}

    # Get the text information
    for k, info in class_details_map().items():
        tag_name = info["tag_name"]
        classes = info["classes"]

        if len(classes) > 1:
            text_el = el.select("{}.{}".format(tag_name, ".".join(classes)))

            if text_el:
                text_el = text_el[0]
        else:
            text_el = el.find(tag_name, attrs={"class": classes})

        if text_el:
            text = text_el.text

            if k == "review_summary":
                text = text.strip('"')

            review[k] = text

    # Get the overall star rating
    stars = find_star_rating(el)

    if stars:
        review["stars"] = stars

    # Get the date the review was posted
    post_date = find_post_date(el)

    if post_date:
        review["post_date"] = post_date

    # Get the job title and status of the reviewer
    job_title_status_info = get_job_title_and_status(el)

    if job_title_status_info:
        review["job_title"] = job_title_status_info["job_title"]
        review["current_employee"] = job_title_status_info["current_employee"]

    # Get the reccomendation, outlook, and CEO approval
    approval_info = get_approval_info(el)

    if approval_info:
        review["approval_info"] = approval_info

    # Get the amount of time an employee has been working at the company
    emp_status_duration_info = get_emp_status_and_duration(el)

    if emp_status_duration_info.get("employment_status"):
        review["employment_status"] = emp_status_duration_info["employment_status"]

    if emp_status_duration_info.get("years_employed"):
        review["years_employed"] = emp_status_duration_info["years_employed"]

    return review


# Finds and retunrs the overall star rating of the company as well as the breakdown in star rating between culture & values, work/life balance, senior management, comp & benefits, and career opportunities
def find_star_rating(el):
    ratings = {}
    overall_stars_el = el.find("span", attrs={"class": "value-title"})

    if (
        not overall_stars_el
        or not overall_stars_el.attrs
        or not overall_stars_el.attrs.get("title")
    ):
        return None

    ratings["overall"] = parse_star_val(overall_stars_el)

    sub_ratings_parent = el.select(".subRatings.module")

    if not sub_ratings_parent:
        return ratings

    sub_ratings_parent = sub_ratings_parent[0]

    breakdown = {}
    for li in sub_ratings_parent.select("li"):
        sub_rating_title_el = li.find("div", attrs={"class": "minor"})
        sub_rating_value_el = li.find("span", attrs={"class": "gdRatings"})

        if sub_rating_title_el and sub_rating_value_el:
            sub_rating_title = (
                sub_rating_title_el.text.lower()
                .replace(" & ", "_")
                .replace(" ", "_")
                .replace("/", "_")
            )
            breakdown[sub_rating_title] = parse_star_val(sub_rating_value_el)

    ratings["breakdown"] = breakdown

    return ratings


# Finds and returns the date that a review was posted
def find_post_date(el):
    date_el = el.find("time", attrs={"class": "date"})

    if not date_el or not date_el.attrs or not date_el.attrs.get("datetime"):
        return None

    return date_el.attrs["datetime"]


# Returns the value of the 'title' class within an element
def parse_star_val(el):
    return str(int(float(el.attrs["title"])))


# Finds and returns the job title and status of the employee posting a review
def get_job_title_and_status(el):
    job_title_status_el = el.find("span", attrs={"class": "authorJobTitle"})
    val = job_title_status_el.text

    info = {}
    if val and len(val.split("-")) == 2:
        status, job_title = [s.strip() for s in val.split("-")]
        info["current_employee"] = "current" in status.lower()
        info["job_title"] = job_title

    return info


# Finds and returns the approval info in three categories: recommend to a friend, approves of CEO, and company outlook
def get_approval_info(el):
    info = {}
    approval_el = el.find("div", attrs={"class": "recommends"})

    if not approval_el:
        return info

    for category in approval_el.select("div.tightLt"):
        rating_parent, category_parent = category.select("div.cell")

        if not rating_parent or not category_parent:
            continue

        rating_el = rating_parent.find("i")
        category_text_el = category_parent.find("span", attrs={"class": "middle"})

        if not rating_el or not category_text_el:
            continue

        category_text = category_for_text(category_text_el.text)

        if not category_text:
            continue

        rating = rating_for_color(rating_el)

        if not rating:
            continue

        info[category_text] = rating

    return info


# Finds and returns the employee status (current/former) and the length of time an employee has been with the company
def get_emp_status_and_duration(el):
    info = {}
    emp_status_duration_el = el.select("p.tightBot.mainText")

    if not emp_status_duration_el:
        return info

    text = emp_status_duration_el[0].text
    lower_text = text.lower()

    employment_values = ["full-time", "part-time", "contract", "intern", "freelance"]

    for val in employment_values:
        if val in lower_text:
            info["employment_status"] = val

    duration_text = re.search("\(([a-z;0-9 ]+)\)", lower_text, re.I)

    if duration_text:
        duration_text = duration_text.group(0)
        years_match = re.search("([0-9]+)", duration_text, re.I)

        if years_match:
            years = years_match.group(0)
        else:
            years = "1"

        if "less" in duration_text:
            duration = "<" + years
        elif "more" in duration_text:
            duration = ">" + years
        else:
            duration = years

        info["years_employed"] = duration

    return info


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


# Helper function to get_approval_info()
def rating_for_color(el):
    color_rating_map = {"red": "-1", "yellow": "0", "green": "1"}

    classes = el.attrs.get("class")

    for color, rating in color_rating_map.items():
        if color in classes:
            return rating

    return None


# Creates a map containing information on classes where the information wanted is text within the given element
def class_details_map():
    return {
        "review_summary": {"tag_name": "span", "classes": ["summary"]},
        "pros": {"tag_name": "p", "classes": ["pros"]},
        "cons": {"tag_name": "p", "classes": ["cons"]},
        "advice_to_mgmt": {"tag_name": "p", "classes": ["adviceMgmt"]},
    }


# Writes the reviews to company_reviews.json in real time
def write_reviews_to_file(reviewsData):
    with open("{}/company_reviews.json".format(DATA_DIR), "w+") as f:
        f.write(json.dumps(reviewsData, sort_keys=True, indent=2))


if __name__ == "__main__":
    force = "--force" in sys.argv
    #main(fetchAllCompanies=force)
    main(fetchAllCompanies=True)
