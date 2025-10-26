from eval_logger import EvalLogger, EvaluationSession
from sqlalchemy.orm import Session

def test_eval_logger():
    eval_logger = EvalLogger("sqlite:///:memory:")
    assert eval_logger is not None
    eval_logger.log_eval(
        prompt="How long it takes to finish?",
        response="It takes 10 minutes to finish.",
        parsed_response="10",
        expected_response="10",
        success=True,
        why="It is a simple question.",
        type_="time",
        user_id="1234",
    )
    eval_logger.log_eval(
        prompt="How long it takes to finish?",
        response="It takes 10 minutes to finish.",
        parsed_response="10",
        expected_response="10",
        success=True,
        why="It is a simple question.",
        type_="time",
        user_id="1234",
    )

    eval_logger.end_session()

    # read from the database
    with Session(eval_logger.db_engine) as session, session.begin():
        session_query = session.query(EvaluationSession).all()
        assert len(session_query) == 1
        assert len(session_query[0].evaluations) == 2