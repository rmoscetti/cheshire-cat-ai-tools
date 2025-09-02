from cat_tools.eval import (
    load_eval_dataset,
    conf_variants,
    hallucination_scorer,
    similarity_scorer,
    repeat_dataset,
    prepare_declarative_memory,
    CatModel,
)
from datetime import datetime
from cat_tools.client import SuperCatClient
import weave
import asyncio
import os
from tqdm.auto import tqdm

os.environ["VERTEXAI_PROJECT"] = "gen-lang-client-0900969241"
os.environ["VERTEXAI_LOCATION"] = "europe-west4"

weave.init("smart-drying-unitus/declarative-eval")

dataset = load_eval_dataset()

asyncio.run(eval_configs(dataset, n_rep=1))


# |export
async def eval_configs(dataset, n_rep=1, model_confs=conf_variants):
    client = SuperCatClient()
    time = datetime.now().strftime("%m-%d %H:%M")
    eval_name = f"{time} Eval"
    prepare_declarative_memory(client)
    evaluation = weave.Evaluation(
        dataset=list(repeat_dataset(dataset, n_rep)),
        scorers=[hallucination_scorer, similarity_scorer],
        name=eval_name,
    )
    # for name, conf in tqdm(model_confs.items(), total=len(model_confs)):
    #     print(f"Evaluating {name} with memory")
    #     model = CatModel(name, conf)
    #     await evaluation.evaluate(
    #         model, __weave={"display_name": f"{eval_name} - {name} memory"}
    #     )
    client.wipe_declarative_memory()
    for name, conf in tqdm(model_confs.items(), total=len(model_confs)):
        print(f"Evaluating {name} without memory")
        model = CatModel(name, conf, has_declarative_memory=False)
        await evaluation.evaluate(
            model, __weave={"display_name": f"{eval_name} - {name} NO memory"}
        )

asyncio.run(eval_configs(dataset, n_rep=1))
