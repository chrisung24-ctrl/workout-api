import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_add_and_stats(client):
    client.post("/logs", json={"exercise": "Squat", "reps": 5, "weight_kg": 100})
    client.post("/logs", json={"exercise": "Squat", "reps": 3, "weight_kg": 120})
    r = client.get("/stats/Squat")
    assert r.json()["max_weight_kg"] == 120
    assert r.json()["total_volume_kg"] == 860


def test_zero_reps_rejected(client):
    r = client.post("/logs", json={"exercise": "Squat", "reps": 0, "weight_kg": 50})
    assert r.status_code == 422