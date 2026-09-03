from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.businesses.model import BusinessMember, BusinessRole
from tests.conftest import register_and_login


def test_create_business(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.post("/api/v1/businesses", headers=headers, json={"name": "Tiệm Nhà Mình"})

    assert response.status_code == 201
    assert response.json()["name"] == "Tiệm Nhà Mình"
    assert response.json()["currency"] == "VND"
    assert response.json()["timezone"] == "Asia/Ho_Chi_Minh"


def test_creator_becomes_owner(client: TestClient, db: Session) -> None:
    headers = register_and_login(client)
    response = client.post("/api/v1/businesses", headers=headers, json={"name": "Tiệm Nhà Mình"})

    membership = db.scalar(
        select(BusinessMember).where(BusinessMember.business_id == UUID(response.json()["id"]))
    )

    assert membership is not None
    assert membership.role == BusinessRole.OWNER


def test_user_lists_only_own_businesses(client: TestClient) -> None:
    owner_headers = register_and_login(client, "owner@example.com")
    other_headers = register_and_login(client, "other@example.com")
    client.post("/api/v1/businesses", headers=owner_headers, json={"name": "Shop Một"})
    client.post("/api/v1/businesses", headers=other_headers, json={"name": "Shop Hai"})

    response = client.get("/api/v1/businesses", headers=owner_headers)

    assert response.status_code == 200
    assert [business["name"] for business in response.json()] == ["Shop Một"]


def test_user_reads_own_business(client: TestClient) -> None:
    headers = register_and_login(client)
    created = client.post(
        "/api/v1/businesses", headers=headers, json={"name": "Shop Của Tôi"}
    ).json()

    response = client.get(f"/api/v1/businesses/{created['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_user_cannot_read_another_business(client: TestClient) -> None:
    owner_headers = register_and_login(client, "owner@example.com")
    other_headers = register_and_login(client, "other@example.com")
    created = client.post(
        "/api/v1/businesses", headers=owner_headers, json={"name": "Shop Riêng"}
    ).json()

    response = client.get(f"/api/v1/businesses/{created['id']}", headers=other_headers)

    assert response.status_code == 404
