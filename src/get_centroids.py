import numpy as np
from sklearn.cluster import MiniBatchKMeans
import json
import helpers as helpers
import pickle
import argparse

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

# load in pickled kmeans model
with open(f"./data/{args.label}kmeans_model.pkl", "rb") as f:
    kmeans = pickle.load(f)

centroids = kmeans.cluster_centers_


cluster_to_reviews = {}
for i in range(10):
    print(f"On iteration {i}.npy")
    with open(f"./data/company_reviews_{i}.json", "r") as f:
        reviews = helpers.extract_sentence_level_reviews(json.load(f), company_info=False)

    embeddings_file = f"./data/{args.label}embeddings/embeddings_{i}.npy"
    embeddings = np.load(embeddings_file)

    closest_indices = [np.argmin(np.linalg.norm(embeddings - centroid, axis=1)) for centroid in centroids]
    representative_reviews = [reviews[idx] for idx in closest_indices]
    for idx, sentence in enumerate(representative_reviews):
        if idx not in cluster_to_reviews:
            cluster_to_reviews[idx] = []
        cluster_to_reviews[idx].append(sentence)
    reviews, embeddings = [], []
        
with open(f"./data/{args.label}centroids.json", "w") as f:
    json.dump(cluster_to_reviews, f, indent=4)


    
