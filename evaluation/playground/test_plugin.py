"""
Evaluation of the Cat agent

evaluation of the cat agent performance for different prompts

uses pytest to run tests, logs the results of the evaluation database
"""
from deploy_plugin import deploy_plugins
from eval_logger import EvalLogger
import pytest
from parse_response import parse_time_to_finish_response
import datetime
from super_cat_client import SuperCatClient
from contextlib import contextmanager


# @pytest.fixture(scope="module")
@contextmanager
def setup_client():
    try:
        client = SuperCatClient()
        # deploy_plugins()
        yield client
    finally:
        client.close()


@pytest.fixture(scope="module")
def eval_logger():
    logger = EvalLogger()
    yield logger
    logger.end_session()

def time_to_finish():
    now = datetime.datetime.now(datetime.timezone.utc)
    next_midnight = (now + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    time_left = (next_midnight - now).total_seconds() // 60
    return str(int(time_left))


@pytest.mark.usefixtures("eval_logger")
@pytest.mark.parametrize(
    "prompt",
    [
        "When will the drying process finish?",
        "How long it takes to finish?",
        "How much time is left?",
        "How long it takes to finish the drying process?",
    ],
)
def test_time_to_finish(eval_logger, prompt):
    with setup_client() as client:
        expected_response = time_to_finish()
        response = client.send(prompt)
        parsed_response = parse_time_to_finish_response(response["content"])
        is_success = parsed_response == expected_response
        details = {
            "prompt": prompt,
            "response": response["content"],
            "parsed_response": parsed_response,
            "expected_response": expected_response,
            "success": is_success,
            "why": response["why"],
            "type_": response["type"],
            "user_id": response["user_id"],
        }
        eval_logger.log_eval(**details)
    assert is_success
