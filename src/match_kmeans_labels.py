import numpy as np
import pandas as pd
import json
from tqdm import tqdm
import helpers as helpers
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sys

# Load the data from the JSON file
with open(f"./data/company_reviews_sample.json", "r") as f:
    reviews = helpers.extract_sentence_level_reviews(json.load(f), company_info=True)

print(f"We have {len(reviews)} reviews.")


#Load in the kmeans labels from the csv file
kmeans_labels = np.genfromtxt('./data/sentence_level_labels.csv', delimiter=',', dtype=int, skip_footer=1)
last_row = np.genfromtxt('./data/sentence_level_labels.csv', delimiter=',', dtype=int, skip_header=2192)
kmeans_labels = np.concatenate((kmeans_labels.reshape(-1), last_row.reshape(-1))).tolist()
print(f"We have {len(kmeans_labels)} labels.")


# iterate through the reviews and add the kmeans label to each review
# Reviews are a currently a list of tuples (company, review)
# We want to add the kmeans label to each review
# We also want to add the sentiment analysis to each review, using the vaderSentiment library
analyzer = SentimentIntensityAnalyzer()
for i in tqdm(range(len(reviews))):
    temp = list(reviews[i])
    temp.append(kmeans_labels[i])
    temp.append(list(analyzer.polarity_scores(reviews[i][1])))
    reviews[i] = tuple(temp)

# Save the reviews to a JSON file
with open(f"./data/company_reviews_kmeans.json", "w") as f:
    json.dump(reviews, f)