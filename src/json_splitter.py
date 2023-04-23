import json

# Load the data from the JSON file
with open("./data/company_reviews.json", "r") as f:
    data = json.load(f)

# Split the data into 10 chunks
chunk_size = len(data) // 10
chunks = [dict(list(data.items())[i:i+chunk_size]) for i in range(0, len(data), chunk_size)]

# Write each chunk to a separate file
for i, chunk in enumerate(chunks):
    with open(f"./data/company_reviews_{i}.json", "w") as f:
        json.dump(chunk, f)