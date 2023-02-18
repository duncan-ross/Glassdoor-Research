import numpy as np
import pandas as pd
import pickle
import code
import string
import os
import json
import re
import time
from definitions import *

from definitions import DATA_DIR, CEM_DIR, REV_PROC_DIR, REV_RAW_DIR
from time import localtime, strftime
from collections import Counter




print(strftime("%Y-%m-%d %H:%M:%S", localtime()))

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

def write_to_pandas(filename):
  # Open the JSON file(s)
  reviews = pd.DataFrame(columns = REVIEW_KEYS)
  total_time_start = time.time()
  with open (DATA_DIR + filename) as f:
    data = json.load(f)

    # Iterate over each company
    count = 1
    for comp, revs in data.items():
      comp_revs = []

      # Iterate over the list of reviews for each company
      for rev in revs:
        # rev_start_time = time.time()

        # Discard reviews without dates
        if rev.get('post_date') is None:
          continue

        # Flatten the review
        flat_review = flatten_json(rev)

        # Get the data from the review
        temp = {}
        for key in REVIEW_KEYS:
          if key == 'years_employed':
              temp[key] = employment_years_to_num(flat_review.get(key))
          else:
            temp[key] = flat_review.get(key)

        temp['company'] = comp

        # Apeend to the reviews
        comp_revs.append(temp)

        # rev_end_time = time.time()
        # print "Process one review:", (rev_end_time - rev_start_time)

      add_comp_start_time = time.time()
      if len(comp_revs) > 0:
        reviews = reviews.append(comp_revs, ignore_index = False)
      add_comp_end_time = time.time()
      print "{}. Time to add {} reviews for {}: {}".format(count, len(comp_revs), comp, add_comp_end_time - add_comp_start_time)
      count += 1

  total_time_end = time.time()
  print "Total time to insert all company reviews:", (total_time_end - total_time_start)

  # Convert the columns to optimize the storage and save the dataframe
  datetime_cols = ['post_date']
  int_cols = ['overall']
  float_cols = ['approves_of_ceo','career_opportunities','comp_benefits','culture_values','current_employee','outlook','recommends','senior_management','work_life_balance']
  reviews[datetime_cols] = reviews[datetime_cols].apply(pd.to_datetime)
  reviews[int_cols] = reviews[int_cols].apply(pd.to_numeric, downcast = 'integer')
  reviews[float_cols] = reviews[float_cols].apply(pd.to_numeric, downcast = 'float')



  # Write the dataframe to file
  reviews.to_pickle(DATA_DIR + filename.replace('.json','.pickle'))

  return


def load_reviews(file_path):
  revs = pd.read_pickle(file_path)
  return revs


def get_control_reviews(sample, rev_limit):

  if rev_limit not in [10, 20, 40, 60, 99]:
    print("Rev limit invalid!")
    code.interact(local = locals())
  
  # Import the control company information from R
  if sample == 'private':
    reviews = load_reviews(REV_RAW_DIR + '/private_company_reviews_update_02_14_19.pickle')
    r_info = pd.read_table(CEM_DIR + '/private_comps_control_' + str(rev_limit) + '_rev.txt')
    rev_index = 100000
    print 'Retrieving reviews for private control sample.'
  elif sample == 'public':
    reviews = load_reviews(REV_RAW_DIR + '/nyse_and_nasdaq_reviews_update_02_14_19.pickle')
    r_info = pd.read_table(CEM_DIR + '/public_comps_control_' + str(rev_limit) + '_rev.txt')
    rev_index = 200000
    print 'Retrieving reviews for public control sample.'
  elif sample == 'treatment':
    reviews = load_reviews(REV_RAW_DIR + '/ipo_company_reviews_update_02_14_19.pickle')
    r_info = pd.read_table(CEM_DIR + '/treatment_comps_' + str(rev_limit) + '_rev.txt')
    rev_index = 0
    print 'Retrieving reviews for treatment sample.'
  else:
    print 'Invalid sample selection: ' + sample
    exit()



  # code.interact(local = locals())
  # reviews['company'] = reviews['company'].map(lambda x: x.strip().lower().rstrip('.').replace(',',''))
  revs = reviews.loc[reviews['company'].isin(r_info['company_name'])]
  revs = pd.merge(left = reviews, right = r_info, left_on = 'company', right_on = 'company_name')

  print(str(revs.company_name.nunique()) + " companies found with " + str(revs.shape[0]) + " reviews.")

  # Get reviews from pandas that match the company name and are within -1/+2 years of the IPO
  revs['ipo_date'] = revs['ipo_date'].apply(pd.to_datetime)
  revs['date_diff'] = revs['post_date'] - revs['ipo_date']
  revs = revs[revs['date_diff'].between('-365 days','730 days',inclusive = True)]
  revs['days_after_ipo'] = revs['date_diff'].dt.days
  def before_after_label(row):
    if row['date_diff'].days < 0:
      return 'before'
    else:
      return 'after'
  revs['before_after'] = revs.apply(lambda row: before_after_label(row), axis = 1)
  
  # # Get the companies that have at least 5 reviews in the before period and 5 in the after period
  rev_count = revs[['company','before_after']].groupby(['company','before_after']).size()
  rev_count = rev_count[rev_count >= 5]
  comp_count = [r[0] for r in rev_count.index]
  cnt = Counter(comp_count)
  comp_keep = [comp for comp, count in cnt.items() if count > 1]
  final_revs = revs.loc[revs['company'].isin(comp_keep)]
  

  # Replace texthe NaN with a 0 for the years employed
  final_revs['years_employed'].fillna(0, inplace = True)

  # Add a review_id
  final_revs.insert(0, 'rev_id', range(rev_index, rev_index + len(final_revs)))


  # code.interact(local = locals())
  # Get only the columns used in the sentiment analysis
  format_cols = ['rev_id', 'pros', 'cons', 'advice_to_mgmt', 'overall', 'before_after', 'company', 'days_after_ipo', 'years_employed', 'job_title']
  final_revs = final_revs[format_cols]

  # code.interact(local = locals())

  # Strip out the unicode that doesn't allow the text to be written to a ascii file in np.savetxt()
  def remove_nonprintable(text):
    if text is not None:
      printable = set(string.printable)
      text = filter(lambda x: x in printable, text)
    return text

  final_revs['pros'] = final_revs['pros'].apply(lambda x: remove_nonprintable(x))
  final_revs['cons'] = final_revs['cons'].apply(lambda x: remove_nonprintable(x))
  final_revs['advice_to_mgmt'] = final_revs['advice_to_mgmt'].apply(lambda x: remove_nonprintable(x))
  final_revs['job_title'] = final_revs['job_title'].apply(lambda x: remove_nonprintable(x))

  print(str(final_revs.shape[0]) + " reviews found for " + str(final_revs.company.nunique()) + " companies after selecting around ipo timeframe.")


  # Save the reviews
  if sample == 'private':
    print 'Saving reviews for private control sample.'
    final_revs.to_pickle(REV_PROC_DIR + '/private_control_reviews_' + str(rev_limit) + '_rev.pickle')
  elif sample == 'public':
    print 'Saving reviews for public control sample.'
    final_revs.to_pickle(REV_PROC_DIR + '/public_control_reviews_' + str(rev_limit) + '_rev.pickle')
  elif sample == 'treatment':
    print 'Saving reviews for treatment sample.'
    final_revs.to_pickle(REV_PROC_DIR + '/treatment_reviews_' + str(rev_limit) + '_rev.pickle')
  else:
    print 'Invalid sample selection: ' + sample
    exit()



get_control_reviews(sample = 'private', rev_limit = 10)
get_control_reviews(sample = 'public', rev_limit = 10)
get_control_reviews(sample = 'treatment', rev_limit = 10)
get_control_reviews(sample = 'private', rev_limit = 20)
get_control_reviews(sample = 'public', rev_limit = 20)
get_control_reviews(sample = 'treatment', rev_limit = 20)
get_control_reviews(sample = 'public', rev_limit = 40)
get_control_reviews(sample = 'private', rev_limit = 40)
get_control_reviews(sample = 'treatment', rev_limit = 40)
get_control_reviews(sample = 'private', rev_limit = 60)
get_control_reviews(sample = 'public', rev_limit = 60)
get_control_reviews(sample = 'treatment', rev_limit = 60)
get_control_reviews(sample = 'private', rev_limit = 99)
get_control_reviews(sample = 'public', rev_limit = 99)
get_control_reviews(sample = 'treatment', rev_limit = 99)
# # Public Reviews Write to Pandas
# write_to_pandas('/nyse_companies/nyse_and_nasdaq_reviews_update_02_14_19.json')
# # Private Reviews Write to Pandas
# write_to_pandas('/private_companies/private_company_reviews_update_02_14_19.json')
# IPO Reviews Write to Pandas
# write_to_pandas('/ipo_companies/ipo_company_reviews_update_02_14_19.json')
code.interact(local = locals())
