import os

DEFAULT_BATCH_SIZE = 100

DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}

USER_AGENT_LIST = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

GLASSDOOR_API_HOST_URL = "http://api.glassdoor.com/api/api.htm"

GLASSDOOR_REVIEWS_BASE_URL = "https://www.glassdoor.com/Reviews"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = "/Users/duncanross/Desktop/Glassdoor-Research/data"

# SMJ_DIR = '/Users/twhittle/Google_Drive/Documents/glassdoor_analysis/smj_submission'
CEM_DIR = DATA_DIR + "/cem_data"

REV_RAW_DIR = DATA_DIR + "/review_data_raw"

REV_PROC_DIR = DATA_DIR + "/review_data_processed"

COMPANY_DATA_FILE = "data/uber_lyft/uber_lyft_companies.xlsx"

COMPANY_FINANCIAL_FILE = "data/monthly_securities_data_compustat.xlsx"

COMPANIES_MAP = DATA_DIR + "companies_map.json"

COMPANY_REVIEWS = DATA_DIR + "company_reviews.json"

EMPLOYEE_STATUS_FILTER = "?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.employmentStatus=FREELANCE&filter.employmentStatus=PART_TIME&filter.employmentStatus=CONTRACT&filter.employmentStatus=INTERN&filter.employmentStatus=REGULAR"

DB_PATH = "postgresql://twhittle:1234567@localhost:5432/glassdoor"

RATING_LABELS_DICT = {
    "work": "work_life_balance",
    "culture": "culture_values",
    "diversity": "diversity_inclusion",
    "career": "career_opportunities",
    "compensation": "comp_benefits",
    "management": "senior_mgmt",
}

REVIEW_KEYS = [
    "post_date",
    "job_title",
    "employment_status",
    "current_employee",
    "years_employed",
    "review_summary",
    "pros",
    "cons",
    "advice_to_mgmt",
    "outlook",
    "recommends",
    "approves_of_ceo",
    "overall",
    "career_opportunities",
    "comp_benefits",
    "culture_values",
    "senior_management",
    "work_life_balance",
]

STAR_COUNT_DICT = {
    "css-1mfncox": 1.0,
    "css-xd4dom": 1.0,
    "css-18v8tui": 2.0,
    "css-1lp3h8x": 2.0,
    "css-e0wqkp": 2.5,
    "css-vl2edp": 3.0,
    "css-k58126": 3.0,
    "css-10u0eun": 3.5,
    "css-1nuumx7": 4.0,
    "css-94nhxw": 4.0,
    "css-s4o194": 4.5,
    "css-s88v13": 5.0,
    "css-11w4osi": 5.0,
}

EXTRANEOUS_WORDS = [
    "co",
    "corp",
    "holdings",
    "holding",
    "cl",
    "llc",
    "inc",
    "associates",
    "ltd",
    "hldng",
]

WRITTEN_REVIEW_TOKENS = [ "advice","cons", "pros"]

