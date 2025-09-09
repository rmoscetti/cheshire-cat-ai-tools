from cat_tools.eval import (
    load_eval_dataset,
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

from cat_tools.client import LLMSettings

settings = LLMSettings()

os.environ["VERTEXAI_PROJECT"] = "gen-lang-client-0900969241"
os.environ["VERTEXAI_LOCATION"] = "europe-west4"

weave.init("smart-drying-unitus/declarative-eval")

dataset = load_eval_dataset()


conf_variants = {
    # "openai_smallest": settings.openai.model_copy(update={"model_name": "gpt-5-nano"}),
    "openai_best": settings.openai.model_copy(update={"model_name": "gpt-5"}),
    # "gemini_smallest": settings.gemini.model_copy(
        # update={"model": "gemini-2.5-flash-lite"}
    # ),
    # "gemini_best": settings.gemini.model_copy(update={"model": "gemini-2.5-pro"}),
    # "gemma_smallest": settings.ollama.model_copy(update={"model": "gemma3:1b"}),
    "gemma_best": settings.ollama.model_copy(update={"model": "gemma3:27b"}),
    # "qwen_smallest": settings.ollama.model_copy(update={"model": "qwen3:0.6b"}),
    "qwen_best": settings.ollama.model_copy(update={"model": "qwen3:32b"}),
    # "deepseek_smallest": settings.ollama.model_copy(
    #     update={"model": "deepseek-r1:1.5b"}
    # ),
    "deepseek_best": settings.ollama.model_copy(update={"model": "deepseek-r1:32b"}),
}

# |export
async def eval_configs(dataset, n_rep=1, model_confs=conf_variants):
    client = SuperCatClient()
    time = datetime.now().strftime("%m-%d %H:%M")
    eval_name = f"{time} Eval"
    # prepare_declarative_memory(client)
    evaluation = weave.Evaluation(
        dataset=list(repeat_dataset(dataset, n_rep)),
        scorers=[similarity_scorer],
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
