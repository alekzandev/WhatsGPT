import json
import tiktoken # for token counting
import numpy as np
from collections import defaultdict

def load_data(jsonl_path: str):

    # Load the dataset
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        dataset = [json.load(line) for line in f]

    # Initial dataset stats
    print("Num examples:", len(dataset))
    print("First example:")
    for message in dataset[0]["messages"]:
        print(message)

if __name__ == "__main__":
    # Load the dataset
    jsonl_path = "data/curated/conversation-prod.jsonl"
    load_data(jsonl_path)
