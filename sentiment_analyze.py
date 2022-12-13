import numpy as np
import pandas as pd
import random
import pickle
import code
import string
import os
import re
import copy
import csv
import nltk

from definitions import DATA_DIR, DB_PATH
from time import localtime, strftime
from collections import Counter

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.sentiment import *
from nltk.sentiment.util import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from scipy.stats import ttest_ind, ttest_rel
from sqlalchemy import create_engine



# Helper function to load reviews
def load_reviews(file_path):
  revs = pd.read_pickle(DATA_DIR + file_path)
  return revs

# Helper function to tokenize the reviews
def tokenize_rev(rev_part, porter_stemmer):

  tok = sent_tokenize(rev_part)
  tok_lower = [sent.lower() for sent in tok]
  tok_stemmed = []

  for sent in tok_lower:
    words = word_tokenize(sent)
    tok_stemmed.append(' '.join(porter_stemmer.stem(w) for w in words))

  if len(tok_stemmed) != len(tok_lower):
    print "[pca]_sent and [pca]_sent_stem of different lengths. Debugging..."
    code.interact(local = locals())

  return tok_lower, tok_stemmed

""" This function pulls in the Glassdoor reviews based on the input parameters and then processes them and saves them to a file. 
If they have already been pulled, then this function just loads the processed file
"""
def process_sents(control, rev_limit):

  # Get the data
  print("Fetching files...")

  if control == "treatment":
    revs_raw = load_reviews('/review_data_processed/treatment_reviews_' + str(rev_limit) + '_rev.pickle')

  elif control == "private":
    revs_raw = load_reviews('/review_data_processed/private_control_reviews_' + str(rev_limit) + '_rev.pickle')

  elif control == "public":
    revs_raw = load_reviews('/review_data_processed/public_control_reviews_' + str(rev_limit) + '_rev.pickle')

  else:
    print("ERROR: INVALID ENTRY FOR CONTROL PARAMETER. Exiting...")
    exit()

  print(strftime("%Y-%m-%d %H:%M:%S", localtime()))

  # Pre-process the reviews by removing stopwords, stemming/lemmatizing, and appending the category to the words
  def sentence_tokenize(revs):
    try:
      print("Preprocessing reviews..")
      stop_words = set(stopwords.words("english"))
      processed_sents = []
      # lemmatizer = WordNetLemmatizer()
      ps = PorterStemmer()
      print(len(revs))

      
      null_pro = 0
      null_con = 0 
      null_adv = 0

      for index, rev in revs.iterrows():
        
        # # Get the categories
        # if rev == '':
        #   continue
        # rev = rev.split('|~|')
        rev_id = rev['rev_id']
        pro = rev['pros']
        con = rev['cons']
        adv = rev['advice_to_mgmt']
        score = rev['overall']
        pre_post = rev['before_after'] 
        # if control == "treatment": rev_id = int(rev[5]) # No longer needed
        company_id = rev['company']
        # industry = rev[7] # No longer needed
        # comp_good_bad = rev[8] # No longer needed
        days_after_ipo = rev['days_after_ipo']
        years_employed = rev['years_employed']
        job_title = rev['job_title']

        if int(rev_id)%1000 == 0:
          print('Rev ID: '+ str(rev_id))

        # ------- NEW CODE (02/19/19) ------------
        # Tokenize the sentences
        if pro is None: 
          pro = ''
          null_pro += 1
        if con is None: 
          con = ''
          null_con += 1
        if adv is None: 
          adv = ''
          null_adv += 1


        pro_sent, pro_sent_stem = tokenize_rev(pro, ps)
        con_sent, con_sent_stem = tokenize_rev(con, ps)
        adv_sent, adv_sent_stem = tokenize_rev(adv, ps)

        # ------- END NEW CODE -------------------

        # For each sentence, stemmed sentence pair, create a new sentence item
        for i in range(0, len(pro_sent)):
          sent = ['pro', pro_sent[i], pro_sent_stem[i], int(score), pre_post, rev_id, company_id, days_after_ipo, years_employed, job_title]
          processed_sents.append(sent)
        for i in range(0, len(con_sent)):
          sent = ['con', con_sent[i], con_sent_stem[i], int(score), pre_post, rev_id, company_id, days_after_ipo, years_employed, job_title]
          processed_sents.append(sent)
        for i in range(0, len(adv_sent)):
          sent = ['adv', adv_sent[i], adv_sent_stem[i], int(score), pre_post, rev_id, company_id, days_after_ipo, years_employed, job_title]
          processed_sents.append(sent)

        # rev_id += 1

      print('Null pros: ' + str(null_pro))
      print('Null cons: ' + str(null_con))
      print('Null advs: ' + str(null_adv))
      return processed_sents

    except KeyboardInterrupt:
      print('exit')
      exit(1)

  sents_processed = []

  # Save and modify the sentences based on whether they are treatment or control. The treatment sentences allow for extra processing. 
  # FOR TREATMENT 
  if control == "treatment":
    
    # If there is a file with the data already saved, load it. Otherwise tokenize and save the data.
    for file in os.listdir(DATA_DIR + '/sentence_data/'):
      if file == ('sents_treatment_' + str(rev_limit) + '_rev.pickle'):
        print('Loading Reviews...')
        sents_processed = load_reviews('/sentence_data/sents_treatment_' + str(rev_limit) + '_rev.pickle')

    if not sents_processed: 
      print('Tokenizing and saving reviews...')
      sents_processed = sentence_tokenize(revs_raw)
      pickle.dump(sents_processed, open(DATA_DIR + '/sentence_data/sents_treatment_' + str(rev_limit) + '_rev.pickle', 'wb'))

    # Generate the filename for the results based on the input parameters
    results_filename = DATA_DIR + '/sentiment_data/sentiment_treatment_' + str(rev_limit) + '_rev.xlsx'
  
  # FOR CONTROL PRIVATE
  elif control == "private":
    
    # If there is a file with the data already saved, load it. Otherwise tokenize and save the data.
    for file in os.listdir(DATA_DIR + '/sentence_data/'):
      if file == ('sents_private_control_' + str(rev_limit) + '_rev.pickle'):
        print('Loading Reviews...')
        sents_processed = load_reviews('/sentence_data/sents_private_control_' + str(rev_limit) + '_rev.pickle')

    if not sents_processed: 
      print('Tokenizing and saving reviews...')
      sents_processed = sentence_tokenize(revs_raw)
      pickle.dump(sents_processed, open(DATA_DIR + '/sentence_data/sents_private_control_' + str(rev_limit) + '_rev.pickle', 'wb'))

    # Generate the filename for the results based on the input parameters
    results_filename = DATA_DIR + '/sentiment_data/sentiment_private_control_' + str(rev_limit) + '_rev.xlsx'

  # FOR CONTROL PUBLIC
  elif control == "public":

    # If there is a file with the data already saved, load it. Otherwise tokenize and save the data.
    for file in os.listdir(DATA_DIR + '/sentence_data/'):
      if file == ('sents_public_control_' + str(rev_limit) + '_rev.pickle'):
        print('Loading Reviews...')
        sents_processed = load_reviews('/sentence_data/sents_public_control_' + str(rev_limit) + '_rev.pickle')

    if not sents_processed: 
      print('Tokenizing and saving reviews...')
      sents_processed = sentence_tokenize(revs_raw)
      pickle.dump(sents_processed, open(DATA_DIR + '/sentence_data/sents_public_control_' + str(rev_limit) + '_rev.pickle', 'wb'))

    # Generate the filename for the results based on the input parameters
    results_filename = DATA_DIR + '/sentiment_data/sentiment_public_control_' + str(rev_limit) + '_rev.xlsx'

  else:
    print("ERROR: INVALID ENTRY FOR CONTROL PARAMETER. Exiting...")
    exit()

  print "Number of sentences:", len(sents_processed)
  return sents_processed, results_filename


""" This function takes two arguments:
      -- sents: the processed sentences returned by process_sents
      -- topics: a dictionary of topic:regular expression that identifies the stemmed words that will be extracted
    It will return a dictionary:
      -- topic_sentiment: key: topic from the reg decitionary
                          value: list of processed sents with sentiment analysis scores appended to each sent
"""
def find_sentiment(sents, topics):
  topic_sentiment = {}
  analyzer = SentimentIntensityAnalyzer()
  # For each topic contained in the word lemmas dict...
  for key,value in topics.iteritems():
    
    # Extract sentences where the regex expression matches the stemmed text. Deep copy so that sentences with multiple topics do not receive multiple sentiment scores. 
    reg = re.compile(value)
    matches = copy.deepcopy([sent for sent in sents if reg.findall(sent[2])])
    
    # Analyze sentiment of each review
    for m in matches:
      vs = analyzer.polarity_scores(m[1])
      m.append(vs)

    # Write the sentiment score to a list
    topic_sentiment[key] = matches

  return topic_sentiment


# Compare sentiment by topic between pre-post IPO
def pre_post_sentiment(topic_sentiment):
  results = {}

  for key, value in topic_sentiment.iteritems():
    
    # Get the pre and post-IPO sentences
    pre = [sent for sent in value if sent[4] == 'before']
    post = [sent for sent in value if sent[4] == 'after']

    # Split into pros, cons, and adv to management and extract the sentiment scores
    pre_pros = [sent[-1]['compound'] for sent in pre if sent[0] == 'pro']
    pre_cons = [sent[-1]['compound'] for sent in pre if sent[0] == 'con']
    pre_adv = [sent[-1]['compound'] for sent in pre if sent[0] == 'adv']

    post_pros = [sent[-1]['compound'] for sent in post if sent[0] == 'pro']
    post_cons = [sent[-1]['compound'] for sent in post if sent[0] == 'con']
    post_adv = [sent[-1]['compound'] for sent in post if sent[0] == 'adv']

    # Perform t-tests betweeen the two samples
    pros_ttest = ttest_ind(pre_pros, post_pros)
    cons_ttest = ttest_ind(pre_cons, post_cons)
    adv_ttest = ttest_ind(pre_adv, post_adv)
    pros_cons_ttest = ttest_ind(pre_pros + pre_cons, post_pros + post_cons)
    all_ttest = ttest_ind(pre_pros + pre_cons + pre_adv, post_pros + post_cons + post_adv)

    # Create lists to be saved
    pros_list = np.array([len(pre_pros), np.mean(pre_pros), len(post_pros), np.mean(post_pros), pros_ttest.statistic, pros_ttest.pvalue])
    cons_list = np.array([len(pre_cons), np.mean(pre_cons), len(post_cons), np.mean(post_cons), cons_ttest.statistic, cons_ttest.pvalue])
    # adv_list = np.array([len(pre_adv), np.mean(pre_adv), len(post_adv), np.mean(post_adv), adv_ttest.statistic, adv_ttest.pvalue])
    pros_cons_list = np.array([len(pre_pros+pre_cons), np.mean(pre_pros+pre_cons), len(post_pros+post_cons), np.mean(post_pros+post_cons), pros_cons_ttest.statistic, pros_cons_ttest.pvalue])
    # all_list = np.array([len(pre_pros+pre_cons+pre_adv), np.mean(pre_pros+pre_cons+pre_adv), len(post_pros+post_cons+pre_adv), np.mean(post_pros+post_cons+pre_adv), all_ttest.statistic, all_ttest.pvalue])
    # ttest_results = np.stack((pros_list, cons_list, adv_list, pros_cons_list, all_list))
    ttest_results = np.stack((pros_list, cons_list, pros_cons_list))
    results[key] = ttest_results

    print "\n\n", key.upper()
    
    # Print numbers of mentions for each topic
    print "Pre-IPO mentions:", len(pre)
    print "Post-IPO mentions:", len(post)

    # Pros analysis
    print "Pros comparison:", pros_ttest
    
    # Cons analysis
    print "Cons comparison:", cons_ttest

    # Adv analysis
    print "Adv comparison:", adv_ttest 

    # Pros + Cons analysis
    print "Pros+Cons comparison:", pros_cons_ttest

    # All categories analysis
    print "All comparison:", all_ttest, "\n"

    # Print out means if the p-value < 0.05
    if np.mean(pre_pros) > np.mean(post_pros) and pros_ttest.pvalue < .05:
      print "Pre-IPO pros mean ("+str(np.mean(pre_pros))+") greater than post-IPO pros mean ("+str(np.mean(post_pros))+")"
    elif pros_ttest.pvalue < .05:
      print "Post-IPO pros mean ("+str(np.mean(post_pros))+") greater than pre-IPO pros mean ("+str(np.mean(pre_pros))+")"
    else:
      pass

    if np.mean(pre_cons) > np.mean(post_cons) and cons_ttest.pvalue < .05:
      print "Post-IPO cons mean ("+str(np.mean(post_cons))+") more negative than pre-IPO cons mean ("+str(np.mean(pre_cons))+")"
    elif cons_ttest.pvalue < .05:
      print "Pre-IPO cons mean ("+str(np.mean(pre_pros))+") less negative than post-IPO cons mean ("+str(np.mean(post_pros))+")"
    else:
      pass

    if np.mean(pre_adv) > np.mean(post_adv) and adv_ttest.pvalue < .05:
      print "Pre-IPO adv mean ("+str(np.mean(pre_adv))+") greater than post-IPO adv mean ("+str(np.mean(post_adv))+")"
    elif  adv_ttest.pvalue < .05:
      print "Post-IPO adv mean ("+str(np.mean(post_adv))+") greater than pre-IPO pros mean ("+str(np.mean(pre_adv))+")"
    else:
      pass

    if np.mean(pre_pros + pre_cons) > np.mean(post_pros + post_cons) and pros_cons_ttest.pvalue < .05:
      print "Pre-IPO pros+cons mean ("+str(np.mean(pre_pros + pre_cons))+") greater than post-IPO pros+cons mean ("+str(np.mean(post_pros + post_cons))+")"
    elif pros_cons_ttest.pvalue < .05:
      print "Post-IPO pros+cons mean ("+str(np.mean(post_pros+ post_cons))+") greater than pre-IPO pros+cons mean ("+str(np.mean(pre_pros + pre_cons))+")"
    else:
      pass

    print "\n"

  return results

""" This function takes two arguments:
      -- sents: the processed sentences returned by process_sents
      -- topics: a dictionary of topic:regular expression that identifies the stemmed words that will be extracted
    It will return a dataframe:
      -- topic_scores: company name, review id, pro_con_adv, before_after, and one column for each sentiment score
"""
def create_r_df(sents, topics):
  # Create a dataframe from sents
  df = pd.DataFrame(sents, columns = ['pro_con_adv', 'sent', 'stem_sent', 'score', 'pre_post', 'rev_id', 'company', 'days_after_ipo', 'years_employed', 'job_title'])
  # df.drop(['industry', 'good_bad'], axis = 1)

  topic_sentiment = {}
  analyzer = SentimentIntensityAnalyzer()
  # For each topic contained in the word lemmas dict...
  for key,value in topics.iteritems():
    print("Finding sentiment for topic: " + key + "...")
    t0 = time.time()
    # Get the matching regex
    reg = re.compile(value)
    # Add the new column
    df[key] = None
    # Iterate over each row
    for index, row in df.iterrows():
      # If the sentence discusses the topic, then get the sentiment score
      if reg.findall(row['stem_sent']):
        compound_score = analyzer.polarity_scores(row['sent'])['compound']
        df.set_value(index, key, compound_score)
    t1 = time.time()
    print "time:", (t1 - t0)
  return df


def write_results_to_csv(filename, results):
  w = csv.writer(open(filename, "wb"))
  for key, val in results.iteritems():
    w.writerow([key])
    for row in val:
      w.writerow(row)
  return

def write_results_to_excel(filename, results):
  writer = pd.ExcelWriter(filename)
  results.to_excel(writer, 'Sheet1')
  writer.save()

def write_results_to_psql(table_name, results):
  print("Starting sql db write...")
  
  t0 = time.time()
  engine = create_engine(DB_PATH)
  
  results.to_sql(table_name, engine, if_exists = 'replace')
  t1 = time.time()
  print "time:", (t1 - t0)



# Perform aggregate statics on the companies' sentiment list

topics = {
  # 'compensation+benefits': "compens|pay|paid|salari|benefit|perk|401k|retir",
  'compensation': "compens|pay|paid|salari",
  'benefits': "benefit|perk|401k|retir|lunch",
  # 'product': "product|technolog|softwar",
  'career_dev': "promot|opportun|career",
  'culture': "cultur",
  # 'wl_bal': "worklife|work life|work environ|atmospher",
  # 'politics': "politic|nepostism|honest|ethic",
  # 'boys_club': "boy|frat|sex",
  'manager': "manag|supervisor|boss",
  # 'manager_v2': "manag|supervisor|",
  # 'startup': "startup",
  'leader': "leader|exec|execut|ceo|cto|coo",
  # 'leader_v2': "leader|exec|execut|ceo|cto|coo|director",
  # 'strategy': "strategi|vision|mission",
  # 'mission': 'mission|purpos',
  # 'communication+transparency': "commun|transpar",
  'communication': "commun",
  'transparency': "transpar",
  # 'integrity': "integr|trust|honest|moral|fair",
  # 'benevolence': "benevol|valu|integr|trust|respect|welfar|care",
  # 'benevolence_new': "benevol|valu|respect|welfar|care",
  # 'benevolence_and_integrity': "valu|integr|trust|respect|welfar|care|honest|moral|fair",
  # 'finance': "cost|financ|wall st|audit|stock|wall street|price",
  'policies': 'polici|procedur|rule|process|bureaucraci|bureaucrat|admin|administr|heirarchi',
  'respect': 'benevol|respect|disrespect|care|uncar|dignit|kind|unkind|appreci|unappreci|condescend', # TW: Consider adding appreciate, disrespect, condescend (08/12/19)
  'DJ': 'compens|pay|paid|salari|benefit|perk|401k|retir|lunch|promot|opportun|career',
  'PJ': 'polici|procedur|rule|process|bureaucraci|bureaucrat|admin|administr|heirarchi|transpar|commun|leader|exec|execut|ceo|cto|coo',
  'IJ': 'manag|supervisor|boss|cultur|benevol|respect|disrespect|care|uncar|dignit|kind|unkind|appreci|unappreci|condescend'
  # 'trust': 'trust|distrust',
  # 'fairness': 'fair|unfair'
  }



# # RUN THE FUNCTIONS
# sents_processed, results_filename = process_sents(control = "public", rev_limit = 10)
# print("Sentence processing complete...")
# r_df = create_r_df(sents_processed, topics)
# code.interact(local = locals())
# print("Writing results to file...")
# write_results_to_excel(results_filename, r_df)
def get_results(control, rev_limit):
  sents_processed, results_filename = process_sents(control = control, rev_limit = rev_limit)
  print("Sentence processing complete...")
  r_df = create_r_df(sents_processed, topics)
  print("Writing results to database...")
  # write_results_to_excel(results_filename, r_df)
  table_name = "sentiment_" + ((control + "_") if control == "treatment" else (control + "_control_")) + str(rev_limit) + "_rev"
  # code.interact(local = locals())
  write_results_to_psql(table_name, r_df)

get_results("public", 10)
get_results("private", 10)
get_results("treatment", 10)
# get_results("public", 20)
# get_results("private", 20)
# get_results("treatment", 20)
# get_results("public", 40)
# get_results("private", 40)
# get_results("treatment", 40)
# get_results("public", 60)
# get_results("private", 60)
# get_results("treatment", 60)
# get_results("public", 99)
# get_results("private", 99)
# get_results("treatment", 99)

# code.interact(local=locals())
# topic_sentiment = find_sentiment(sents_processed, topics)
# results = pre_post_sentiment(topic_sentiment)

# TODO:
# 1. Add a review id to the sentences - DONE
# 2. Create a new function analyze_sentiment that returns a pandas dataframe with the company name, review id, pro_con_adv, before_after, and one column for each sentiment score. 

# Write the results to a file
# write_results_to_csv(results_filename, results)


code.interact(local = locals())




