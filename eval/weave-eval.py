import weave

from super_cat_client import SuperCatClient
from cheshire_cat_api.config import Config
import re
from drymulator_client.api.default import current_state_state_current_get
from drymulator_client.client import Client
import asyncio

config = Config()
drymulator_url = "http://localhost:7435"


class CatModel(weave.Model):
    @weave.op()
    async def predict(self, prompt: str) -> dict:
        with SuperCatClient(config) as client:
            response = client.send(prompt)
        return response


weave.init("intro-example")

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


# print(drymulator_weight_eval({"text": "the result is 10"}))

dataset_example = [
    {
        "id": 0,
        "prompt": "Query the drying system to get the current weight of the product",
    },
    {
        "id": 1,
        "prompt": "What is the current weight of the product in the drying system?",
    },
    {"id": 2, "prompt": "How much does the product weigh in the drying system?"},
    # {
    #     "id": 3,
    #     "prompt": "What is the weather today?"
    # }
]

evaluation = weave.Evaluation(
    dataset=dataset_example,
    scorers=[drymulator_weight_eval],
)

print(asyncio.run(evaluation.evaluate(model)))
