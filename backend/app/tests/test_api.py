from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.core.database import Base, engine

@pytest.fixture(scope="session", autouse=True)
def create_db():
    Base.metadata.create_all(bind=engine)
    yield

client = TestClient(app)

def test_ping():
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"message": "pong"}

def test_students():
    resp = client.get("/students")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    names = {s["name"] for s in data}
    assert {"Sehaj", "Jesmeen"}.issubset(names)
