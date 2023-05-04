import json
import numpy as np
import torch
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
import argparse

from helpers import extract_reviews

argp = argparse.ArgumentParser()
argp.add_argument("--num", type=int, default=0)
args = argp.parse_args()

# Load BERT model
model_name = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

if torch.cuda.is_available(): 
    device = torch.device("cuda")
    model = model.to(device)
else:
    device = torch.device("cpu")

# Load the data from the JSON file
with open(f"./data/company_reviews_{args.num}.json", "r") as f:
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

# Initialize an empty array for the embeddings
all_embeddings = []

# Process reviews in smaller batches
batch_size = 128
for i in tqdm(range(0, len(reviews), batch_size), desc="Processing reviews"):
    batch_reviews = reviews[i:i+batch_size]
    inputs = tokenizer(batch_reviews, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        inputs.to(device)
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        all_embeddings.extend(embeddings)

# Convert the list of embeddings to a numpy array
all_embeddings = np.array(all_embeddings)

# Dimensionality reduction
pca = PCA(n_components=2)
reduced_embeddings = pca.fit_transform(embeddings)

# Clustering
kmeans = KMeans(n_clusters=6, random_state=0)
kmeans.fit(reduced_embeddings)
labels = kmeans.labels_


# Assign the reviews to the corresponding clusters
clustered_reviews = {i: [] for i in range(6)}
#for review, label in tqdm(zip(reviews, labels), desc="Assigning reviews to clusters", total=len):
for review, label in zip(reviews, labels):
    clustered_reviews[label].append(review)

# Save the clustered reviews to separate files
for cluster_id, cluster_reviews in clustered_reviews.items():
    with open(f"./data/reviews_{args.num}/cluster_{cluster_id}.txt", "w", encoding="utf-8") as f:
        for review in cluster_reviews:
            f.write(review + "\n\n")

import numpy as np

# Calculate the centroids of each cluster
centroids = kmeans.cluster_centers_

print("Embeddings shape:", reduced_embeddings.shape)
print("Centroids shape:", centroids.shape)

from sklearn.metrics import pairwise_distances_argmin_min

# Find the index of the closest review embedding to each centroid
closest_indices = [np.argmin(np.linalg.norm(reduced_embeddings - centroid, axis=1)) for centroid in centroids]

# Retrieve the most representative review for each cluster
representative_reviews = [reviews[idx] for idx in closest_indices]

# Print the representative reviews
for i, review in enumerate(representative_reviews):
    print(f"Cluster {i}: {review}\n")