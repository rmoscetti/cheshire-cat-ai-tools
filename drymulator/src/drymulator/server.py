from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends
from sqlmodel import (
    Field,
    Session,
    SQLModel,
    create_engine,
    func,
    select,
)
from datetime import datetime
import csv
import importlib.resources
from pydantic_settings import BaseSettings


# automatically loads settings from the enviroment variables
class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"


settings = Settings()


class ConfigBase(SQLModel):
    start_time: Optional[datetime] = Field(default=datetime.now())
    time_speed: Optional[float] = Field(default=10.0)


class Config(ConfigBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ConfigPublic(ConfigBase):
    pass


class ConfigCreate(ConfigBase):
    pass


class StateBase(SQLModel):
    time_seconds: int
    fraction_initial: float
    weight: float


class State(StateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class StatePublic(StateBase):
    pass


engine = create_engine(settings.database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def read_state_test_data(session: Session):
    """Reads data from a CSV file and returns a list of dictionaries."""
    with importlib.resources.open_text("drymulator", "test_data.csv") as file:
        for row in csv.DictReader(file):
            session.add(State.model_validate(row))
    session.commit()


def maybe_create_config(session: Session):
    existing_config = session.exec(select(Config)).first()
    if not existing_config:
        session.add(Config())
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        maybe_create_config(session)
        read_state_test_data(session)
    yield


# --- FastAPI App ---

app = FastAPI(lifespan=lifespan)


@app.post("/command/config")
async def config(
    config: ConfigCreate,
    session: Session = Depends(get_session),
) -> bool:
    existing_config = session.exec(select(Config)).first()
    config = Config.model_validate(config)
    if existing_config:
        existing_config.start_time = config.start_time
        existing_config.time_speed = config.time_speed
    else:
        session.add(config)
    session.commit()
    return True


@app.get("/state/current")
async def current_state(session: Session = Depends(get_session)) -> StatePublic:
    config = session.exec(select(Config)).first()
    actual_time = datetime.now()
    diff_seconds = (actual_time - config.start_time).total_seconds()
    state = session.exec(
        select(State).order_by(func.abs(State.time_seconds - diff_seconds))
    ).first()
    return state


# need to find a better name for this
@app.get("/state/time")
async def state_time(
    second_after: int, session: Session = Depends(get_session)
) -> StatePublic:
    state = session.exec(
        select(State).order_by(func.abs(State.time_seconds - second_after))
    ).first()
    return state
