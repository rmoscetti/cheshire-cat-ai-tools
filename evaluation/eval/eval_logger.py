"""
Logs the results of the evaluation to a database.
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    JSON,
    Float,
    DateTime,
    create_engine,
)
import subprocess
from typing import List
from dotenv import dotenv_values

import cheshire_cat_api as ccat
from pyprojroot import here

config = ccat.Config()
cat_client = ccat.CatClient(config)
env = dotenv_values(here(".env"))
env = env | dotenv_values(here(".env.local"))


class Base(DeclarativeBase):
    pass


class EvaluationSession(Base):
    """
    Stores information about a evaluation session.
    """

    __tablename__ = "evaluation_session"

    id: Mapped[int] = Column(Integer, primary_key=True)
    commit: Mapped[str] = Column(String)
    model: Mapped[str] = Column(String)
    plugin_settings: Mapped[dict] = Column(JSON)
    llm_name: Mapped[str] = Column(String)
    llm_temperature: Mapped[float] = Column(Float)
    embedder_model: Mapped[str] = Column(String)
    start_time: Mapped[datetime] = Column(DateTime)
    end_time: Mapped[datetime] = Column(DateTime, nullable=True)

    evaluations: Mapped[List["Evaluation"]] = relationship(back_populates="session")


class Evaluation(Base):
    """
    Stores information about a single evaluation.
    """

    __tablename__ = "evaluation"

    id: Mapped[int] = Column(Integer, primary_key=True)
    session_id: Mapped[int] = Column(Integer, ForeignKey("evaluation_session.id"))
    prompt: Mapped[str] = Column(String)
    response: Mapped[str] = Column(String)
    parsed_response: Mapped[str] = Column(String)
    expected_response: Mapped[str] = Column(String)
    success: Mapped[bool] = Column(Integer)
    type: Mapped[str] = Column(String)
    user_id: Mapped[str] = Column(String)
    why_input: Mapped[str] = Column(String)
    why_intermediate: Mapped[dict] = Column(JSON)
    why_agent_output: Mapped[dict] = Column(JSON)

    session: Mapped[EvaluationSession] = relationship(back_populates="evaluations")
    episodic_memory: Mapped[List["EpisodicMemory"]] = relationship(back_populates="evaluation")
    declarative_memory: Mapped["DeclarativeMemory"] = relationship(back_populates="evaluation")
    procedural_memory: Mapped[List["ProceduralMemory"]] = relationship(back_populates="evaluation")
    model_interaction: Mapped[List["ModelInteraction"]] = relationship(back_populates="evaluation")


class EpisodicMemory(Base):
    """
    Stores information about a single evaluation.
    """

    __tablename__ = "episodic_memory"

    id: Mapped[int] = Column(Integer, primary_key=True)
    evaluation_id: Mapped[int] = Column(Integer, ForeignKey("evaluation.id"))    
    meta_source: Mapped[str] = Column(String)
    meta_when: Mapped[datetime] = Column(DateTime)
    page_content: Mapped[str] = Column(String)
    type: Mapped[str] = Column(String)
    score: Mapped[float] = Column(Float)

    evaluation: Mapped[Evaluation] = relationship(back_populates="memory_episodic")

class DeclarativeMemory(Base):
    __tablename__ = "declarative_memory"
    id: Mapped[int] = Column(Integer, primary_key=True)
    evaluation_id: Mapped[int] = Column(Integer, ForeignKey("evaluation.id"))

    evaluation: Mapped[Evaluation] = relationship(back_populates="memory_declarative")

class ProceduralMemory(Base):
    __tablename__ = "procedural_memory"
    id: Mapped[int] = Column(Integer, primary_key=True)
    evaluation_id: Mapped[int] = Column(Integer, ForeignKey("evaluation.id"))
    meta_source: Mapped[str] = Column(String)
    meta_type: Mapped[str] = Column(String)
    meta_trigger_type: Mapped[str] = Column(String)
    meta_when: Mapped[datetime] = Column(DateTime)
    page_content: Mapped[str] = Column(String)
    type: Mapped[str] = Column(String)
    score: Mapped[float] = Column(Float)

    evaluation: Mapped[Evaluation] = relationship(back_populates="memory_procedural")

class ModelInteraction(Base):
    __tablename__ = "model_interaction"
    id: Mapped[int] = Column(Integer, primary_key=True)
    evaluation_id: Mapped[int] = Column(Integer, ForeignKey("evaluation.id"))
    meta_type: Mapped[str] = Column(String)
    source: Mapped[str] = Column(String)
    prompt: Mapped[str] = Column(String)
    input_tokens: Mapped[int] = Column(Integer)
    started_at: Mapped[datetime] = Column(DateTime)
    reply: Mapped[dict] = Column(JSON)




class EvalLogger:
    """
    
    """

    def __init__(self, db_url: str = None):
        db_url = db_url or env["DATABASE_URL"]
        self.db_engine = create_engine(db_url)
        Base.metadata.create_all(self.db_engine)
        self.init_eval_session()

    def init_eval_session(self):
        commit = self.get_current_commit()
        cat_settings = self.model_cat_settings()
        start_time = datetime.now()
        self.session = EvaluationSession(
            commit=commit,
            model=cat_settings["llm_name"],
            plugin_settings=cat_settings,
            llm_name=cat_settings["llm_name"],
            llm_temperature=cat_settings["llm_temperature"],
            embedder_model=cat_settings["embedder_model"],
            start_time=start_time,
        )

    def get_current_commit(self) -> str:
        try:
            commit_hash = (
                subprocess.check_output(["git", "rev-parse", "HEAD"])
                .strip()
                .decode("utf-8")
            )
            return commit_hash
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving commit hash: {e}")
            return None

    def model_cat_settings(self) -> dict:
        """
        Get the model and plugin settings from the cat client.
        """
        settings = cat_client.settings.get_settings()["settings"]
        res = {}
        for setting in settings:
            match setting["name"]:
                case "LLMOpenAIChatConfig":
                    res["llm_name"] = setting["value"]["model_name"]
                    res["llm_temperature"] = setting["value"]["temperature"]
                case "EmbedderOpenAIConfig":
                    res["embedder_model"] = setting["value"]["model"]
                # ensure settings are valid
                case "llm_selected":
                    assert setting["value"]["name"] == "LLMOpenAIChatConfig"
                case "embedder_selected":
                    assert setting["value"]["name"] == "EmbedderOpenAIConfig"
                case "active_plugins":
                    assert "cheshire_cat_ai_toolkit" in setting["value"]
        return res

    def log_eval(
        self,
        prompt: str,
        response: str,
        parsed_response: str,
        expected_response: str,
        success: bool,
        why: dict,
        type_: str,
        user_id: str,
    ):
        
        episodic_memory = [
            EpisodicMemory(
                meta_source=memory['metadata']["source"],
                meta_when=memory['metadata']["when"],
                page_content=memory["content"],
                type=memory["type"],
                score=memory["score"],
            )
            for memory in why['memory']["episodic"]
        ]

        declarative_memory = DeclarativeMemory()

        procedural_memory = [
            ProceduralMemory(
                meta_source=memory['metadata']["source"],
                meta_type=memory['metadata']["type"],
                meta_trigger_type=memory['metadata']["trigger_type"],
                meta_when=memory['metadata']["when"],
                page_content=memory["content"],
                type=memory["type"],
                score=memory["score"],
            )
            for memory in why['memory']["procedural"]
        ]

        
        
        eval = Evaluation(
            session_id=self.session.id,
            prompt=prompt,
            response=response,
            parsed_response=parsed_response,
            expected_response=expected_response,
            success=success,
            why_input=why["input"],
            type=type_,
            user_id=user_id,
            episodic_memory=episodic_memory,
            declarative_memory=declarative_memory,
            procedural_memory=procedural_memory,
            why_intermediate=why["intermediate_steps"],
            why_agent_output=why["agent_output"],
        )
        self.session.evaluations.append(eval)
        return eval

    def end_session(self):
        self.session.end_time = datetime.now()
        # save the session to the database
        with Session(self.db_engine) as session, session.begin():
            session.add(self.session)
            session.commit()
