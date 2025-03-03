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

DATABASE_URL = "sqlite:///./test.db"


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


engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def read_state_test_data(session: Session):
    """Reads data from a CSV file and returns a list of dictionaries."""
    with importlib.resources.open_text("drymulator.server", "test_data.csv") as file:
        for row in csv.DictReader(file):
            session.add(State.model_validate(row))
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        read_state_test_data(session)
    yield


# --- FastAPI App ---

app = FastAPI(lifespan=lifespan)


@app.post("/command/start")
async def start(
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
async def get_current_state(session: Session = Depends(get_session)) -> StatePublic:
    config = session.exec(select(Config)).first()
    actual_time = datetime.now()
    diff_seconds = (actual_time - config.start_time).total_seconds()
    state = session.exec(
        select(State).order_by(func.abs(State.time_seconds - diff_seconds))
    ).first()
    return state


# need to find a better name for this
@app.get("/state/time")
async def get_state(
    second_after: int, session: Session = Depends(get_session)
) -> StatePublic:
    state = session.exec(
        select(State).order_by(func.abs(State.time_seconds - second_after))
    ).first()
    return state
