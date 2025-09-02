from cat_tools.eval import eval_configs, load_eval_dataset
from cat_tools.setup_declarative_memory import setup_declarative_memory
import weave
import asyncio
import os

os.environ['VERTEXAI_PROJECT'] = "gen-lang-client-0900969241"
os.environ['VERTEXAI_LOCATION'] = "europe-west4"

weave.init("smart-drying-unitus/declarative-eval")


setup_declarative_memory()
dataset = load_eval_dataset()

asyncio.run(eval_configs(dataset, n_rep=1))