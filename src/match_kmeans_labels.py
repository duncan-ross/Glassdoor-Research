import numpy as np
import pandas as pd
import json
from tqdm import tqdm
import helpers as helpers
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import argparse
import os

argp = argparse.ArgumentParser()
argp.add_argument("--data", type=str, default="company_reviews_sample.json")
argp.add_argument('--sentence_level', action='store_true')
argp.add_argument('--review_level', dest='sentence_level', action='store_false')
argp.set_defaults(sentence_level=False)
args = argp.parse_args()

if args.sentence_level:
    args.label = "sentence_level_kmeans"
else:
    args.label = "review_level_kmeans"

# Load the data from the JSON file
with open(f"./data/{args.data}", "r") as f:
    if args.sentence_level:
        reviews = helpers.extract_sentence_level_reviews(json.load(f), company_info=True)
    else:
        reviews = helpers.extract_review_level_reviews(json.load(f), company_info=True)


#Load in the kmeans labels from the csv file
with open(f'./data/{args.label}', 'r') as f:
    num_rows = sum(1 for line in f)

kmeans_labels = np.genfromtxt(f'./data/{args.label}_labels.csv', delimiter=',', dtype=int, skip_footer=1)
last_row = np.genfromtxt(f'./data/{args.label}_labels.csv', delimiter=',', dtype=int, skip_header=num_rows - 1)
kmeans_labels = np.concatenate((kmeans_labels.reshape(-1), last_row.reshape(-1))).tolist()

# Sanity check
assert len(reviews) == len(kmeans_labels)

# Write the output to a csv file
companies_map = pd.read_csv('./data/companies_map.csv')
analyzer = SentimentIntensityAnalyzer()
with open(f"data/{args.label}_output.csv", "w") as outfile:
    outfile.write("company_index,company_name,date,kmeans_label,neg_score,neu_score,pos_score,compound_score\n")
    for i in tqdm(range(len(reviews))):
        company_index = companies_map.loc[companies_map['company_name'] == reviews[i][0]]["index"].values[0]
        score = analyzer.polarity_scores(reviews[i][2]).values()
        outfile.write(f"{company_index},{reviews[i][0]},{reviews[i][1]},{kmeans_labels[i]},{','.join(map(str, score))}\n")
