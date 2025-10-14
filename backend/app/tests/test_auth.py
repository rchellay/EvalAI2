from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models import User
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True, scope="function")
def setup_db():
    # Recreate tables for isolation (simple approach for now)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup users table only
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()

def test_register_and_login():
    # Register
    resp = client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 200, resp.text
    # Login
    resp = client.post("/auth/login", json={
        "username": "alice",
        "password": "secret123"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid():
    resp = client.post("/auth/login", json={
        "username": "ghost",
        "password": "wrong"
    })
    assert resp.status_code == 401
