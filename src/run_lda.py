import json
import helpers
import numpy as np
import pandas as pd
import lda
import lda.datasets
import argparse
from sklearn.feature_extraction.text import CountVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tqdm

argp = argparse.ArgumentParser()
argp.add_argument("--data", type=str, default="company_reviews.json")
argp.add_argument('--sentence_level', action='store_true')
argp.add_argument('--review_level', dest='sentence_level', action='store_false')
argp.set_defaults(sentence_level=True)
args = argp.parse_args()


if args.sentence_level:
    args.label = "sentence_level_"
else:
    args.label = "review_level_"

# Load the data from the JSON file
with open(f"./data/{args.data}", "r") as f:
    if args.sentence_level:
        reviews_CI = helpers.extract_sentence_level_reviews(json.load(f), company_info=True)
        reviews = [review[2] for review in reviews_CI]
    else:
        reviews_CI = helpers.extract_review_level_reviews(json.load(f), company_info=True)
        reviews = [review[2] for review in reviews_CI]

print(f"We have {len(reviews)} reviews.")

count_vect = CountVectorizer()
tdm = count_vect.fit_transform(reviews)
vocab = count_vect.get_feature_names_out()


model = lda.LDA(n_topics=6, n_iter=15000, random_state=1)
model.fit(tdm)

topic_word = model.topic_word_
n_top_words = 8
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
    print('Topic {}: {}'.format(i, ' '.join(topic_words)))

doc_topic = model.doc_topic_
for i in range(10):
    print("{} (top topic: {})".format(reviews[i], doc_topic[i].argmax()))

companies_map = pd.read_csv('./data/companies_map.csv')
name2idx = dict(zip(companies_map.company_name, companies_map.index))
analyzer = SentimentIntensityAnalyzer()
with open(f"data/{args.label}lda_output.csv", "w") as outfile:
    outfile.write("company_index,company_name,date,lda_label,neg_score,neu_score,pos_score,compound_score\n")
    for i in tqdm(range(len(reviews))):
        company_index = name2idx[reviews[i][0]]
        score = analyzer.polarity_scores(reviews[i][2]).values()
        outfile.write(f"{company_index},{reviews[i][0]},{reviews[i][1]},{doc_topic[i].argmax()},{','.join(map(str, score))}\n")
