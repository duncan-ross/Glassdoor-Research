#! /bin/bash

python src/generate_embeddings.py --sentence_level
python src/kmeans_on_embeddings.py --sentence_level
python src/match_kmeans_labels.py --sentence_level
python src/get_centroids.py --sentence_level

python src/generate_embeddings.py --review_level
python src/kmeans_on_embeddings.py --review_level
python src/match_kmeans_labels.py --review_level
python src/get_centroids.py --review_level