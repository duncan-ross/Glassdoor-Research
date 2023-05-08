import pandas as pd
#from helpers import extract_reviews
import json
from tqdm import tqdm

# Load the data from the JSON file
with open(f"./data/company_reviews.json", "r") as f:
    data = json.load(f)

# Extract the reviews
reviews = []
for company in tqdm(data.values(), desc="Extracting reviews"):
    for review in company:
        if review == "PAGE_FAILURE":
            continue
        if review["pros"] is not None:
            reviews.append(review["pros"].split(".|!|?|\n"))
        if review["cons"] is not None:
            reviews.append(review["cons"].split(".|!|?|\n"))
        if review["advice"] is not None:
            reviews.append(review["advice"].split(".|!|?|\n"))

# Filter out empty or None reviews
reviews = [review for review in reviews if review]

"""### Data Preprocessing"""
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import nltk
nltk.download('wordnet')

stemmer = SnowballStemmer('english')

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

# convert reviews to a Pandas DataFrame
reviews_df = pd.DataFrame(reviews, columns=['review'])

# apply the preprocess function to each review using the 'map' function
processed_docs = reviews_df['review'].map(preprocess)

"""### Bag of words on the dataset"""

dictionary = gensim.corpora.Dictionary(processed_docs)
dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

"""### TF-IDF"""

from gensim import corpora, models

tfidf = models.TfidfModel(bow_corpus)

corpus_tfidf = tfidf[bow_corpus]

from pprint import pprint

for doc in corpus_tfidf:
    pprint(doc)
    break

"""### Running LDA using Bag of Words"""

lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=6, id2word=dictionary, passes=2, workers=2)

for idx, topic in lda_model.print_topics(-1):
    print('Topic: {} \nWords: {}'.format(idx, topic))

"""Cool! Can you distinguish different topics using the words in each topic and their corresponding weights?

### Running LDA using TF-IDF
"""

lda_model_tfidf = gensim.models.LdaMulticore(corpus_tfidf, num_topics=6, id2word=dictionary, passes=2, workers=4)

for idx, topic in lda_model_tfidf.print_topics(-1):
    print('Topic: {} Word: {}'.format(idx, topic))

"""### Classification of the topics

### Performance evaluation by classifying sample document using LDA Bag of Words model
"""

#for index, score in sorted(lda_model[bow_corpus[4310]], key=lambda tup: -1*tup[1]):
#    print("\nScore: {}\t \nTopic: {}".format(score, lda_model.print_topic(index, 10)))

"""Our test document has the highest probability to be part of the topic on the top.

### Performance evaluation by classifying sample document using LDA TF-IDF model
"""

#for index, score in sorted(lda_model_tfidf[bow_corpus[4310]], key=lambda tup: -1*tup[1]):
#    print("\nScore: {}\t \nTopic: {}".format(score, lda_model_tfidf.print_topic(index, 10)))

"""Our test document has the highest probability to be part of the topic on the top.

### Testing model on unseen document
"""

#unseen_document = 'How a Pentagon deal became an identity crisis for Google'
#bow_vector = dictionary.doc2bow(preprocess(unseen_document))

#for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
#    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))