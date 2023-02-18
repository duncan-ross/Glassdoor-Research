import json
import re
from pprint import pprint
from definitions import *
import code
import time
from pandas.io.json import json_normalize
import pandas as pd
import xlrd
import datetime
import db_helper
import pickle
from glassdoor import db
from models import Companies, Reviews, CompanyReviews, CompanyFinancials
from sqlalchemy import inspect
from sqlalchemy.engine import reflection



# Converts the json produced in company_reviews to a list of dictionaries
def upsert_companies_and_reviews():
   
  # Create a new db session
  session = db.session

  # Initialize the reivew_data
  review_data = []

  # Get each company that was searched for in Glassdoor
  companies = get_excel_data(COMPANY_DATA_FILE, True,  COMPANIES_MAP)

  # Get the json of company reviews
  with open (COMPANY_REVIEWS) as f:
    data = json.load(f)

  # Iterate over each company
  for comp in companies:

    start = time.time()

    # Get the company name since it's a unique identifier
    params = {}
    params['company_name']=comp.get('company_name')

    # Insert the company to the companies table
    company, comp_is_new = db_helper.find_or_initialize_by(Companies, params, comp, session)
    
    session.commit()
    print 'Company name: %s, Company ID: %s, is_new: %s' % (company.company_name, company.id, comp_is_new)

    # Get the company name
    name = company.company_name

    # Track the number of reviews 
    count = 0
      
    # Iterate over each review if it's a new company
    if data.get(name) and comp_is_new:

      for rev in data.get(name):

        # Discard reviews without dates
        if rev.get('post_date') is None:
          continue

        # Flatten the review
        flat_start = time.time()
        flat_review = flatten_json(rev)
        flat_end = time.time()
        print "Flattend review time:", (flat_end - flat_start)

        # Get the data from the review
        gather_start = time.time()
        temp = {}
        for key in REVIEW_KEYS:
          if key == 'years_employed':
              temp[key] = employment_years_to_num(flat_review.get(key))
          else:
            temp[key] = flat_review.get(key)
        gather_end = time.time()
        print "Get review data time:", (gather_end - gather_start)

        # Insert the review into the review table
        insert_rev_start = time.time()
        review, rev_is_new = db_helper.find_or_initialize_by(Reviews, temp, temp, session)
        session.commit()
        insert_rev_end = time.time()
        print "Insert review into Reviews time:", (insert_rev_end - insert_rev_start)

        # Insert the review into the company_review table
        insert_comp_rev_start = time.time()
        comp_rev = {}
        comp_rev['company_id'] = company.id
        comp_rev['review_id'] = review.id
        company_review = db_helper.find_or_initialize_by(CompanyReviews, comp_rev, comp_rev, session)
        session.commit()
        insert_comp_rev_end = time.time()
        print "Insert review into Company_Reviews time:", (insert_comp_rev_end - insert_comp_rev_start)
        code.interact(local = locals())

        # Increment the count upon successful insertion to the reviews table
        count = count + 1


      company = db_helper.update(company, {'num_reviews': count}, session)
      print 'Number of Reviews: %d' % count
      session.commit()
      end = time.time()
      print "Inserted and committed in time:", (end - start)

    else:
      print 'No Reviews'
      # company = db_helper.update(company, {'num_reviews': count}, session)
      session.commit()

  return review_data


# Helper function that writes a list to file for later reading. 
def write_list_to_file(mylist):
  with open('{}/financial_data.txt'.format(DATA_DIR), 'wb') as f:
    pickle.dump(mylist, f)


# Gets company info from an excel file as a list of dictionaries with the column header as the keys and each row as the values
def get_excel_data(excel_file, is_company, json_file = None):
  
  # Open the excel file and get the first sheet
  wb = xlrd.open_workbook(excel_file)
  sh = wb.sheet_by_index(0)

  # If it is a company data file, open the companies_map that contains the URL
  if is_company and json_file is not None:
    with open (json_file) as f:
      companies_map = json.load(f)

  output = []

  # Iterate over the rows and create a new dictionary for each row
  print "Getting data from %s rows..." % sh.nrows
  print "Num cols: %s" % sh.ncols
  for i in range(1, sh.nrows):
    d = {}
    
    if i%100 == 0:
      print "Retrieved %s rows..." % i

    for j in range(sh.ncols):


      # Get the individual cell and check if it is a date cell. If it is, get the date, otherwise, just extract the value.
      cell = sh.col(j)[i]

      if cell.ctype is 3:
        tuple_datetime = xlrd.xldate_as_tuple(cell.value, wb.datemode)
        date_cell = datetime.date(tuple_datetime[0], tuple_datetime[1], tuple_datetime[2])
        d[sh.col(j)[0].value] = str(date_cell)

      else:
        if cell.value == 'N.A.' or cell.value == '':
          d[sh.col(j)[0].value] = None
        else:
          d[sh.col(j)[0].value] = cell.value

    # Get the URL from the json if it exists
    if is_company:
      d['company_url'] = companies_map.get(d['company_name'],{}).get('reviews_url')

    output.append(d)

    if not is_company:
      write_list_to_file(output)

  return output



# Flatten JSON to get only the final key in nested dictionaries
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


# Converts the text provided of the number of years employed to a number
def employment_years_to_num(em_years):

  # Find if the number of years is greater than or less than
  if em_years is None:
    return None
  elif re.search('>', em_years):
    return float(re.findall('\d+',em_years)[0]) + .5
  elif re.search('<', em_years):
    return float(re.findall('\d+',em_years)[0]) - .5
  else:
    return None


# Upsert financial data
def upsert_financial_data():

  # Get a new database sessions
  session = db.session

  # Get the financial data
  print "Fetching financial data..."
  # fin_dat = get_excel_data(COMPANY_FINANCIAL_FILE, False)

  # !! Right now the financial data needs to be in financial_data.txt. If it is not, then get_excel_data() needs to be run. 
  with open('{}/financial_data.txt'.format(DATA_DIR), 'wb') as f:
    fin_dat = pickle.load(f)


  print "Inserting financial data..."
  # For each row, find the company id and then insert it into the database
  count = 0
  comp_not_found = []
  for row in fin_dat:
    comp = db_helper.find(Companies, {'ticker': row.get('ticker')}, session)
    if comp is None:
      comp_not_found.append(row.get('ticker'))
    row['company_id'] = comp.id
    fin_row, is_new = db_helper.find_or_initialize_by(CompanyFinancials, row, row, session)
    session.commit()
    if is_new: count += 1

  print 'Inserted %s rows of financial data' % count
  print 'Did not find company_id for the following tickers: %s' % comp_not_found



# Run the upsert function
upsert_companies_and_reviews()

# Run the upsert financial data function
# upsert_financial_data()
