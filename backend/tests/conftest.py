import os
from collections.abc import Iterator

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.modules.assistant import model as assistant_models  # noqa: F401
from app.modules.businesses import model as business_models  # noqa: F401
from app.modules.expenses import model as expense_models  # noqa: F401
from app.modules.products import model as product_models  # noqa: F401
from app.modules.sales import model as sales_models  # noqa: F401
from app.modules.users import model as user_models  # noqa: F401

test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def reset_database() -> Iterator[None]:
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def db() -> Iterator[Session]:
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, email: str = "owner@example.com") -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "StrongPass123!", "full_name": "Chủ Shop"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "StrongPass123!"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
