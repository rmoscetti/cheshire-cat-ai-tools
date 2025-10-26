from cat_tools.eval import eval_configs, load_eval_dataset
import weave
import asyncio
import os
from cat_tools.client import LLMSettings

settings = LLMSettings()

os.environ['VERTEXAI_PROJECT'] = "gen-lang-client-0900969241"
os.environ['VERTEXAI_LOCATION'] = "europe-west4"

conf_variants = {
    "openai_smallest": settings.openai.model_copy(update={"model_name": "gpt-5-nano"}),
    # "openai_best": settings.openai.model_copy(update={"model_name": "gpt-5"}),
    "gemini_smallest": settings.gemini.model_copy(
        update={"model": "gemini-2.5-flash-lite"}
    ),
    # "gemini_best": settings.gemini.model_copy(update={"model": "gemini-2.5-pro"}),
    "gemma_smallest": settings.ollama.model_copy(update={"model": "gemma3:1b"}),
    # "gemma_best": settings.ollama.model_copy(update={"model": "gemma3:27b"}),
    "qwen_smallest": settings.ollama.model_copy(update={"model": "qwen3:0.6b"}),
    # "qwen_best": settings.ollama.model_copy(update={"model": "qwen3:32b"}),
    "deepseek_smallest": settings.ollama.model_copy(
        update={"model": "deepseek-r1:1.5b"}
    ),
    # "deepseek_best": settings.ollama.model_copy(update={"model": "deepseek-r1:32b"}),
}

weave.init("smart-drying-unitus/declarative-eval")

dataset = load_eval_dataset()

asyncio.run(eval_configs(dataset, n_rep=1, model_confs = conf_variants))