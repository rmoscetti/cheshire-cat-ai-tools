from cheshire_cat_api import CatClient
import requests
from tqdm import tqdm
from pyprojroot import here
import pandas as pd

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


def read_sentences():
    path = here("eval/declarative_memory.csv")
    df = pd.read_csv(path)
    return df['risposta'].tolist()
    

def setup_declarative_memory():
    wipe_declarative_memory()
    sentences = read_sentences()
    put_sentences(sentences)

if __name__ == "__main__":
    setup_declarative_memory()
