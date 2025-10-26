import weave

from super_cat_client import SuperCatClient
from cheshire_cat_api.config import Config
import re
from drymulator_client.api.default import current_state_state_current_get
from drymulator_client.client import Client
import asyncio
import pandas as pd
from pyprojroot import here
from weave.scorers import HallucinationFreeScorer, EmbeddingSimilarityScorer
import os

os.environ['VERTEXAI_PROJECT'] = "gen-lang-client-0900969241"
os.environ['VERTEXAI_LOCATION'] = "europe-west4"

config = Config()
drymulator_url = "http://localhost:7435"


class CatModel(weave.Model):
    @weave.op()
    async def predict(self, prompt: str) -> dict:
        with SuperCatClient(config) as client:
            response = client.send(prompt)
        return response


weave.init("smart-drying-unitus/declarative-eval")

model = CatModel()
sentence = "Query the drying system to get the current weight of the product"
# print(model.predict(sentence)["text"])


@weave.op()
def drymulator_weight_eval(output: dict) -> dict:
    is_correct = False
    try:
        llm_weight = float(re.search(r"\d+(\.\d+)?", output["text"])[0])
        with Client(drymulator_url) as client:
            state = current_state_state_current_get.sync(client=client)
            real_weight = state.weight
        is_correct = abs(llm_weight - real_weight) < 0.1
    except ValueError:
        print("Failed to extract weight from response")
        is_correct = False
    finally:
        print(f"Is correct: {is_correct}")
        return {"correct": is_correct}


def load_eval_dataset():
    path = here("eval/declarative_memory.csv")
    df = pd.read_csv(path)
    return [
        {"id": i, "prompt": row["domanda"], "input": row["domanda"], "context": row["risposta"], 'target': row["risposta"]}
        for i, row in df.iterrows()
    ]


# print(drymulator_weight_eval({"text": "the result is 10"}))

# dataset_example = [
#     {
#         "id": 0,
#         "prompt": "Query the drying system to get the current weight of the product",
#     },
#     {
#         "id": 1,
#         "prompt": "What is the current weight of the product in the drying system?",
#     },
#     {"id": 2, "prompt": "How much does the product weigh in the drying system?"},
#     # {
#     #     "id": 3,
#     #     "prompt": "What is the weather today?"
#     # }
# ]

dataset = load_eval_dataset()[:10]

hallucination_scorer = HallucinationFreeScorer(
    model_id="vertex_ai/gemini-2.5-pro",
)


from collections.abc import Sequence
from typing import Any

import numpy as np
from pydantic import Field

import weave
from weave.scorers.default_models import OPENAI_DEFAULT_EMBEDDING_MODEL
from weave.scorers.scorer_types import LLMScorer


class CatEmbeddingSimilarityScorer(LLMScorer):
    """
    Computes the cosine similarity between the embeddings of a model output and a target text.

    This scorer leverages the LLM's embedding capabilities (via litellm.aembedding) to generate vector
    representations for both the provided output and target. It then calculates the cosine similarity between
    these two vectors.

    Attributes:
        model_id (str): The embedding model identifier. Defaults to `OPENAI_DEFAULT_EMBEDDING_MODEL`.
        threshold (float): A float value (between -1 and 1) representing the minimum cosine similarity
            necessary to consider the two texts as similar.

    """

    model_id: str = OPENAI_DEFAULT_EMBEDDING_MODEL
    threshold: float = Field(0.5, description="The threshold for the similarity score")

    @weave.op
    async def score(self, *, output: str, target: str, **kwargs: Any) -> Any:
        # Ensure the threshold is within the valid range for cosine similarity.
        assert -1 <= self.threshold <= 1, "`threshold` should be between -1 and 1"

        model_embedding, target_embedding = await self._compute_embeddings(
            output['text'], target
        )
        return self._cosine_similarity(model_embedding, target_embedding)

    async def _compute_embeddings(
        self, output: str, target: str
    ) -> tuple[list[float], list[float]]:
        embeddings = await self._aembedding(self.model_id, [output, target])
        return embeddings.data[0]["embedding"], embeddings.data[1]["embedding"]

    def _cosine_similarity(self, vec1: Sequence[float], vec2: Sequence[float]) -> dict:
        """Compute the cosine similarity between two vectors.

        Args:
            vec1: The first vector.
            vec2: The second vector.

        Returns:
            A dictionary containing:
                - "similarity_score": The cosine similarity as a float.
                - "is_similar": A boolean indicating if the similarity_score is greater than or equal to the threshold.
        """
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        cosine_sim = np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))
        cosine_sim = float(cosine_sim)
        return {
            "similarity_score": cosine_sim,
            "is_similar": cosine_sim >= self.threshold,
        }

similarity_scorer = CatEmbeddingSimilarityScorer(
    model_id="vertex_ai/gemini-embedding-001",
    threshold=0.8,
)

evaluation = weave.Evaluation(
    dataset=dataset,
    scorers=[hallucination_scorer, similarity_scorer],
)

print(asyncio.run(evaluation.evaluate(model)))
