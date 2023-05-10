import numpy as np
from sklearn.cluster import MiniBatchKMeans
from tqdm import tqdm
import sys
import pickle
import csv
import argparse

# Initialize MiniBatchKMeans object with desired hyperparameters
n_clusters = 6
batch_size = 10000
kmeans = MiniBatchKMeans(n_clusters=n_clusters, batch_size=batch_size)

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

# Loop over all 10 files of embeddings
for i in range(10):
    embeddings_file = f"./data/{args.label}embeddings/embeddings_{i}.npy"
    
    # Define generator that yields batches of embeddings from file
    print(f"On file embeddings_{i}.npy")
    def embeddings_generator(file):
        embeddings = np.load(file)

        for batch in np.array_split(embeddings, len(embeddings) // batch_size):
            #print(batch.shape)
            yield batch
    
    # Fit MiniBatchKMeans to the embeddings in the file
    for batch in embeddings_generator(embeddings_file):
        kmeans.partial_fit(batch)


print("Generating labels now:")
# Get cluster labels for all the embeddings
all_labels = []
for i in range(10):
    embeddings_file = f"./data/{args.label}embeddings/embeddings_{i}.npy"
    embeddings = np.load(embeddings_file)
    print(f"On file embeddings_{i}.npy")
    labels = kmeans.predict(embeddings)
    all_labels.append(labels)

# Concatenate all the labels into a single array
all_labels = np.concatenate(all_labels)
print(f"We have {len(all_labels)} labels.")

# Save the model
with open(f"./data/{args.label}kmeans_model.pkl", "wb") as f:
    pickle.dump(kmeans, f)

# Save the labels to a csv file
with open(f"./data/{args.label}kmeans_labels.csv", "w", newline='') as f:
    writer = csv.writer(f, delimiter=',')
    for i in range(0, len(all_labels), 10000):
        writer.writerow(all_labels[i:i+10000])