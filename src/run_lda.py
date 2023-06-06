import json
import helpers
import numpy as np
import lda
import lda.datasets
from sklearn.feature_extraction.text import CountVectorizer



with open(f"./data/company_reviews_sample.json", "r") as f:
    reviews = helpers.extract_sentence_level_reviews(json.load(f), company_info=False)
print(f"We have {len(reviews)} reviews.")
print(reviews[0])

count_vect = CountVectorizer()
tdm = count_vect.fit_transform(reviews)
vocab = count_vect.get_feature_names_out()


model = lda.LDA(n_topics=6, n_iter=1500, random_state=1)
model.fit(tdm)

topic_word = model.topic_word_
n_top_words = 8
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
    print('Topic {}: {}'.format(i, ' '.join(topic_words)))

doc_topic = model.doc_topic_
for i in range(10):
    print("{} (top topic: {})".format(reviews[i], doc_topic[i].argmax()))


