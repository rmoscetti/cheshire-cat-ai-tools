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
    delete
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
    is_active: Optional[bool] = Field(default=True)


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


class HistoryState(StateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CurrentState(StateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class StatePublic(StateBase):
    pass


engine = create_engine(settings.database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def read_state_test_data(session: Session):
    """Reads data from a CSV file and returns a list of dictionaries."""
    # if table already exist skip this
    if session.exec(select(HistoryState)).first():
        return
    with importlib.resources.open_text("drymulator", "test_data.csv") as file:
        for row in csv.DictReader(file):
            session.add(HistoryState.model_validate(row))
    session.commit()


def maybe_create_config(session: Session):
    existing_config = session.exec(select(Config)).first()
    if not existing_config:
        session.add(Config())
    session.commit()

def reset_current_state(session: Session):
    session.exec(delete(CurrentState))
    state = CurrentState.model_validate(session.exec(select(HistoryState).order_by(HistoryState.time_seconds)).first())
    session.add(state)


def init_state_config(session: Session):
    config = session.exec(select(Config)).first()
    if not config:
        config = Config()
        session.add(config)
    state = session.exec(select(CurrentState)).first()
    if not state:
        reset_current_state(session)
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        maybe_create_config(session)
        read_state_test_data(session)
        init_state_config(session)
    yield


def update_current_state(session: Session) -> CurrentState:
    config = session.exec(select(Config)).first()
    if not config.is_active:
        return session.exec(select(CurrentState)).first()
    
    actual_time = datetime.now()
    diff_seconds = (actual_time - config.start_time).total_seconds() * config.time_speed
    target_state = session.exec(
        select(HistoryState).order_by(func.abs(HistoryState.time_seconds - diff_seconds))
    ).first()

    current_state = CurrentState.model_validate(target_state)
    
    session.add(target_state)
    session.commit()
    return current_state

# --- FastAPI App ---

app = FastAPI(lifespan=lifespan)


@app.post("/command/reset")
async def config(
    config: ConfigCreate,
    session: Session = Depends(get_session),
) -> bool:
    session.exec(delete(Config))
    config = Config.model_validate(config)
    session.add(config)
    reset_current_state(session)
    session.commit()
    return True

@app.post("/command/pause")
async def pause(session: Session = Depends(get_session)) -> bool:
    config = session.exec(select(Config)).first()
    config.is_active = False
    session.add(config)
    session.commit()
    return True

@app.post("/command/start")
async def restart(session: Session = Depends(get_session)) -> bool:
    config = session.exec(select(Config)).first()
    config.is_active = True
    session.add(config)
    session.commit()
    return True

@app.get("/state/current")
async def current_state(session: Session = Depends(get_session)) -> StatePublic:
    state = update_current_state(session)
    return StatePublic.model_validate(state)

# need to find a better name for this
@app.get("/state/time")
async def state_time(
    second_after: int, session: Session = Depends(get_session)
) -> StatePublic:
    state = session.exec(
        select(HistoryState).order_by(func.abs(HistoryState.time_seconds - second_after))
    ).first()
    return state

@app.get("/state/get-config")
async def get_config(session: Session = Depends(get_session)) -> ConfigPublic:
    config = session.exec(select(Config)).first()
    return ConfigPublic.model_validate(config)