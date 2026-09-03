from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def test_register(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": " OWNER@Example.com ",
            "password": "StrongPass123!",
            "full_name": "Chủ Shop",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "owner@example.com"
    assert "password" not in response.json()


def test_duplicate_email_rejected(client: TestClient) -> None:
    payload = {"email": "owner@example.com", "password": "StrongPass123!", "full_name": "A"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_login_success(client: TestClient) -> None:
    register_and_login(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == 3600


def test_invalid_login_rejected(client: TestClient) -> None:
    register_and_login(client)

    response = client.post(
        "/api/v1/auth/login", json={"email": "owner@example.com", "password": "wrong"}
    )

    assert response.status_code == 401


def test_authenticated_me(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"
