import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test_collab.db"

sys.path.insert(0, os.path.dirname(__file__))

os.environ["DB_HOST"] = "localhost"
os.environ["DB_PASSWORD"] = ""
os.environ["DB_NAME"] = "test_collab"

from database import Base, get_db
from main import app
from auth import hash_password


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Override DATABASE_URL for tests."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_collab.db"):
        os.remove("./test_collab.db")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client):
    """Create a test user and return credentials."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }
    resp = client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 200
    return user_data


@pytest.fixture
def auth_token(client, test_user):
    """Login and return JWT token."""
    resp = client.post("/api/auth/login", json=test_user)
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def authorized_client(client, auth_token):
    """Return a client with auth header."""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client


@pytest.fixture
def test_project(authorized_client):
    """Create a test project and return its ID."""
    resp = authorized_client.post("/api/projects", json={
        "name": "Test Project",
        "description": "A test project",
    })
    assert resp.status_code == 200
    return resp.json()
