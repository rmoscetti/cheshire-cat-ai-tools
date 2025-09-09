from cat_tools.rerun_eval import get_missing_df, run_missing, weave_client
import asyncio
missing = get_missing_df(weave_client)
asyncio.run(run_missing(missing))