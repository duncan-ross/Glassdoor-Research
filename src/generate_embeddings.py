import json
import numpy as np
import torch
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
import argparse
import os
import re
import helpers as helpers

# Load BERT model
model_name = 'distilbert-base-uncased'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

if torch.cuda.is_available(): 
    device = torch.device("cuda")
    model = model.to(device)
else:
    device = torch.device("cpu")

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


for k in range(10):
    # Load the data from the JSON file
    with open(f"./data/company_reviews_{k}.json", "r") as f:
        if args.sentence_level:
            reviews = helpers.extract_sentence_level_reviews(json.load(f), company_info=False)
        else:
            reviews = helpers.extract_review_level_reviews(json.load(f), company_info=False)

    print(f"We have {len(reviews)} reviews.")

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

    # Define the directory path
    directory = f"./data/{args.label}embeddings/"

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    np.save(f"{directory}/embeddings_{k}.npy", all_embeddings)

    all_embeddings = None
