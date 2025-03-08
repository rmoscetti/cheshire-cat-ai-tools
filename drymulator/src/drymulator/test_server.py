from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from .server import app, ConfigCreate
import time

client = TestClient(app)


def test_reset():
    config = jsonable_encoder(
        ConfigCreate(time_speed=0.1)
    )  # make sure there is no update before we query
    response = client.post("/command/reset", json=config)
    assert response.status_code == 200

    response = client.get("/state/config")
    assert response.status_code == 200
    assert response.json() == config

    state0 = client.get("/state/time", params={"second_after": 0}).json()
    assert state0["time_seconds"] == 0
    current_state = client.get("/state/current").json()
    assert current_state == state0


def test_not_active():
    config = ConfigCreate(
        time_speed=100, is_active=False
    )  # fast time speed to can see change
    client.post("/command/reset", json=jsonable_encoder(config))
    # pause see no change
    # config = client.post("/command/pause").json()
    # print(config)
    prev_val = client.get("/state/current").json()
    time.sleep(1)
    new_val = client.get("/state/current").json()
    assert new_val == prev_val


def test_pause():
    config = ConfigCreate(
        time_speed=100, is_active=True
    )  # fast time speed to can see change
    client.post("/command/reset", json=jsonable_encoder(config))
    prev_val = client.get("/state/current").json()
    # expect to see to change after pause
    config = client.post("/command/pause").json()
    time.sleep(5)
    new_val = client.get("/state/current").json()
    assert new_val == prev_val


def test_resume():
    config = ConfigCreate(
        time_speed=100, is_active=False
    )  # fast time speed to can see change
    client.post("/command/reset", json=jsonable_encoder(config))
    # expect to see to change after resume
    config = client.post("/command/resume").json()
    prev_val = client.get("/state/current").json()
    time.sleep(1)
    new_val = client.get("/state/current").json()
    assert new_val != prev_val
    assert new_val["time_seconds"] > prev_val["time_seconds"]
