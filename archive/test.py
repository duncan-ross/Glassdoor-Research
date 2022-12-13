import numpy as np
import pandas as pd
import os
import nltk
import random
import pickle
import code
import string

from statistics import mode
from definitions import DATA_DIR
from time import localtime, strftime
from collections import Counter
from scipy.stats import ttest_ind, ttest_rel, mannwhitneyu, ranksums
import matplotlib.pyplot as plt

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.classify import ClassifierI
from nltk.classify.scikitlearn import SklearnClassifier

from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier, LassoCV
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, roc_auc_score, accuracy_score, confusion_matrix, r2_score
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA

print(strftime("%Y-%m-%d %H:%M:%S", localtime()))

# # CODE USED TO OPEN A CLASSIFIER THAT HAS BEEN SAVED
# classifier_f = open(DATA_DIR + "/reviews_text/classifiers_score/score_trinary_bothall_ind_6000_feat_14431_train_stem_labels_bigramsnaive_bayes.pickle","rb")
# classifier = pickle.load(classifier_f)
# classifier_f.close()

# def save_most_informative_features(nb_clf, n = 100):
#   # Determine the most relevant features, and display them.
#   mif = []
#   cpdist = nb_clf._feature_probdist
#   print('Most Informative Features')

#   for (fname, fval) in nb_clf.most_informative_features(n):
#     def labelprob(l):
#       return cpdist[l, fname].prob(fval)

#     labels = sorted([l for l in nb_clf._labels
#                      if fval in cpdist[l, fname].samples()],
#                     key=labelprob)
#     if len(labels) == 1:
#       continue
#     l0 = labels[0]
#     l1 = labels[-1]
#     if cpdist[l0, fname].prob(fval) == 0:
#       ratio = 'INF'
#     else:
#       ratio = (cpdist[l1, fname].prob(fval) / cpdist[l0, fname].prob(fval))
#     mif.append((fname, fval, l1, l0, ratio))

#   return mif 

# nb_mif = save_most_informative_features(classifier)


def mif_analyze(mif, file_name, swint, labels, n_gram):
  # Fetch the appropriate processed reviews dataframe
  if swint:
    if labels:
      if n_gram == 1:
        revs = pd.read_pickle("/Users/twhittle/Google_Drive/Documents/glassdoor-py/data/reviews_text/processed_text/pd_processed_revs_both_swint_labels_words.pickle")
      else:
        revs = pd.read_pickle("/Users/twhittle/Google_Drive/Documents/glassdoor-py/data/reviews_text/processed_text/pd_processed_revs_both_swint_labels_bigrams.pickle")
      # Get only the sampled revs
    else:
      print("This hasn't been saved yet")
      code.interact(local = locals())
  else:
    if labels:
      if n_gram == 1:
        revs = pd.read_pickle("/Users/twhittle/Google_Drive/Documents/glassdoor-py/data/reviews_text/processed_text/pd_processed_revs_both_all_labels_words.pickle")
      else:
        revs = pd.read_pickle("/Users/twhittle/Google_Drive/Documents/glassdoor-py/data/reviews_text/processed_text/pd_processed_revs_both_all_labels_bigrams.pickle")
    else:
      print("This hasn't been saved yet")
      code.interact(local = locals())      

  # Get the list of all words/bigrams listed in the most important features
  words = mif['words'].dropna()
  if n_gram > 1:
    words = [w[0] + " " + w[1] for w in words]

  # Add the before avg freq and after avg freq to mif
  mif['avg_before'] = 0
  mif['avg_after'] = 0

  # For each word/bigram, create a column that indicates whether it appears in the processed reviews
  for w in words: 
    revs[w] = revs['processed_rev'].str.contains(w, case=False).astype(int)

  if 'bad' in file_name or 'good' in file_name:
    # Split the reviews into before and after. Aggregate counts by company and get freqnecy. 
    mentions = revs.groupby(['before_after', 'company_id', 'comp_good_bad']).sum()
    num_revs = revs.groupby(['before_after', 'company_id', 'comp_good_bad'])['company_id'].count()
    freq_dist = mentions.div(num_revs, axis = 0).reset_index()  
    
    # Compute the t-tests
    # get a list of all columns in the dataframe without the Group column
    column_list = [x for x in freq_dist.columns if x not in ('before_after','company_id', 'comp_good_bad', 'score', 'sampled')]

    # create an empty dictionary
    t_test_results = {}

    # loop over column_list and execute code explained above
    for column in column_list:
      
      # Look at the difference in distribution for all companies
      group1 = freq_dist.where(freq_dist.before_after == 'before').dropna()[column]
      group2 = freq_dist.where(freq_dist.before_after == 'after').dropna()[column]
      if n_gram > 1:
        mif.at[mif.words == tuple(column.split()), 'avg_before'] = np.mean(group1)
        mif.at[mif.words == tuple(column.split()), 'avg_after'] = np.mean(group2)
      t_test_results[(column, 'good' if 'good' in file_name else 'bad')] = ttest_ind(group1, group2)

      # # Look at the difference in distribution for bad companies
      # group1_bad = freq_dist[(freq_dist['comp_good_bad'] == 'bad') & (freq_dist['before_after'] == 'before')].dropna()[column]
      # group2_bad = freq_dist[(freq_dist['comp_good_bad'] == 'bad') & (freq_dist['before_after'] == 'after')].dropna()[column]
      # t_test_results[(column, column + '_bad', 'bad')] = ttest_ind(group1_bad, group2_bad)

      # # Look at the difference in distribution for good companies
      # group1_good = freq_dist[(freq_dist['comp_good_bad'] == 'good') & (freq_dist['before_after'] == 'before')].dropna()[column]
      # group2_good = freq_dist[(freq_dist['comp_good_bad'] == 'good') & (freq_dist['before_after'] == 'after')].dropna()[column]
      # t_test_results[(column, column + '_good', 'good')] = ttest_ind(group1_good, group2_good)

    results_df = pd.DataFrame.from_dict(t_test_results,orient='Index')
    results_df.columns = ['statistic','pvalue']
    results_df['temp'] = results_df.index
    results_df[['words', 'comp_good_bad']] = results_df['temp'].apply(pd.Series)
    results_df.drop('temp', axis = 1, inplace = True)


    if n_gram > 1:
      results_df.words = results_df.words.str.split(' ')
      results_df.words = results_df.words.apply(lambda x: tuple(x))
    
    mif['avg_diff'] = mif['avg_after'] - mif['avg_before']
    mif = mif[['words','fval','lab1','lab2','ratio', 'avg_before', 'avg_after', 'avg_diff']].drop_duplicates()
    mif = pd.merge(mif, results_df, how = 'left', left_on = 'words', right_on = 'words')
    # mif_both = mif_both[['words','fval','lab1','lab2','ratio']].drop_duplicates()
    # mif = pd.merge(mif, results_df[results_df['comp_good_bad'] == 'both'], how = 'left', left_on = 'words', right_on = 'words')
    # mif_good = mif_good[['words','fval','lab1','lab2','ratio']].drop_duplicates()
    # mif_good = pd.merge(mif, results_df[results_df['comp_good_bad'] == 'good'], how = 'left', left_on = 'words', right_on = 'words')
    # mif_bad = mif_bad[['words','fval','lab1','lab2','ratio']].drop_duplicates()
    # mif_bad = pd.merge(mif, results_df[results_df['comp_good_bad'] == 'bad'], how = 'left', left_on = 'words', right_on = 'words')
    # mif = pd.concat(mif_both, mif_good, mif_bad)


    # Print the the words where the t-test has p < .10
    p10_mif = mif.loc[mif['pvalue'] < .1]
    print(p10_mif)

    # Get the freq_dist for the mif with a significant p-value
    if n_gram > 1:
      sig_cols = [' '.join(words) for words in p10_mif.words.tolist()]
    else:
      sig_cols = p10_mif.words.tolist()
    sig_cols.extend(('before_after', 'company_id', 'sampled', 'comp_good_bad'))
    # sig_freq_dist = freq_dist[sig_cols]
    sig_freq_dist = freq_dist

    # Write the new mif and freq_dist to file
    mif.to_pickle(DATA_DIR + "/reviews_text/most_important_features/" + file_name)
    mif.to_csv(DATA_DIR + "/reviews_text/most_important_features/" + file_name.replace('pickle','csv'))
    sig_freq_dist.to_csv(DATA_DIR + "/reviews_text/most_important_features/" + file_name.replace('mif', 'freq_dist').replace('pickle','csv'))

    return mif
  
  else:
    # Do something else
    print("Not good/bad classifier...")
    return 0

  

for file in os.listdir(DATA_DIR + "/reviews_text/most_important_features/"):
  if file.endswith('pickle'):
    print(file)
    mif = pd.read_pickle(DATA_DIR + "/reviews_text/most_important_features/" + file)
    if mif.empty:
      print("DF is empty!")
    else:
      swint = True if 'swint' in file else False
      labels = True if 'labels' in file else False
      n_gram = 1 if 'words' in file else 2
      if '1yr' in file:
        temp = mif_analyze(mif, file, swint, labels, n_gram)

# file = 'mif_score_binary_both_swint_4000_feat_3852_train_stem_labels_words_naive_bayes.pickle'
# mif = pd.read_pickle(DATA_DIR + "/reviews_text/most_important_features/" + file)
# code.interact(local = locals())
# swint = True if 'swint' in file else False
# labels = True if 'labels' in file else False
# n_gram = 1 if 'words' in file else 2
# temp = mif_analyze(mif, file, swint, labels, n_gram)


print("Code complete.")
print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
# code.interact(local = locals())