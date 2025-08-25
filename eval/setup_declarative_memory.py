from cheshire_cat_api import CatClient
import requests
from tqdm import tqdm

client = CatClient()

def wipe_declarative_memory():
    return client.memory.wipe_single_collection("declarative")

sentences = [
    "Drying is an important process",
    "Dried fruit tastes great"
]

def put_sentence(sentence: str):
    """Put sentence in declarative memory"""
    url = 'http://localhost:1865/memory/collections/declarative/points'
    json_data = {
        "content": sentence,
        "metadata": {}
    }
    response = requests.post(url, json=json_data)
    response.raise_for_status()
    return response

def put_sentences(sentences: list[str]):
    results = []
    for sentence in tqdm(sentences, desc="Adding to declarative memory"):
        result = put_sentence(sentence)
        results.append(result)
    return results

def main():
    wipe_declarative_memory()
    put_sentences(sentences)

if __name__ == "__main__":
    main()
