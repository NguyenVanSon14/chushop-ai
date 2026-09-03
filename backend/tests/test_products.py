from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.businesses.model import BusinessMember, BusinessRole
from app.modules.users.model import User
from tests.conftest import register_and_login


def create_business(client: TestClient, headers: dict[str, str], name: str = "Shop Một") -> str:
    response = client.post("/api/v1/businesses", headers=headers, json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def product_payload(sku: str = "SP-001") -> dict[str, object]:
    return {
        "name": "Áo thun",
        "sku": sku,
        "selling_price": 299000,
        "cost_price": 120000,
        "is_active": True,
    }


def test_product_crud(client: TestClient) -> None:
    headers = register_and_login(client)
    business_id = create_business(client, headers)

    created = client.post(
        f"/api/v1/businesses/{business_id}/products",
        headers=headers,
        json=product_payload(" sp-001 "),
    )
    assert created.status_code == 201
    assert created.json()["sku"] == "SP-001"
    assert created.json()["selling_price"] == 299000
    product_id = created.json()["id"]

    listed = client.get(f"/api/v1/businesses/{business_id}/products", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [product_id]

    detail = client.get(f"/api/v1/businesses/{business_id}/products/{product_id}", headers=headers)
    assert detail.status_code == 200

    updated = client.patch(
        f"/api/v1/businesses/{business_id}/products/{product_id}",
        headers=headers,
        json={"selling_price": 319000, "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["selling_price"] == 319000
    assert updated.json()["is_active"] is False

    deleted = client.delete(
        f"/api/v1/businesses/{business_id}/products/{product_id}", headers=headers
    )
    assert deleted.status_code == 204
    assert (
        client.get(
            f"/api/v1/businesses/{business_id}/products/{product_id}", headers=headers
        ).status_code
        == 404
    )


def test_money_requires_nonnegative_integers(client: TestClient) -> None:
    headers = register_and_login(client)
    business_id = create_business(client, headers)
    payload = product_payload()
    payload["selling_price"] = 299000.5

    float_response = client.post(
        f"/api/v1/businesses/{business_id}/products", headers=headers, json=payload
    )
    payload["selling_price"] = -1
    negative_response = client.post(
        f"/api/v1/businesses/{business_id}/products", headers=headers, json=payload
    )

    assert float_response.status_code == 422
    assert negative_response.status_code == 422


def test_sku_is_unique_per_business(client: TestClient) -> None:
    headers = register_and_login(client)
    first_business = create_business(client, headers, "Shop Một")
    second_business = create_business(client, headers, "Shop Hai")

    first = client.post(
        f"/api/v1/businesses/{first_business}/products",
        headers=headers,
        json=product_payload("sku-1"),
    )
    duplicate = client.post(
        f"/api/v1/businesses/{first_business}/products",
        headers=headers,
        json=product_payload("SKU-1"),
    )
    other_business = client.post(
        f"/api/v1/businesses/{second_business}/products",
        headers=headers,
        json=product_payload("SKU-1"),
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert other_business.status_code == 201


def test_products_are_tenant_isolated(client: TestClient) -> None:
    owner_headers = register_and_login(client, "owner@example.com")
    outsider_headers = register_and_login(client, "outsider@example.com")
    business_id = create_business(client, owner_headers)
    product = client.post(
        f"/api/v1/businesses/{business_id}/products",
        headers=owner_headers,
        json=product_payload(),
    ).json()

    assert (
        client.get(
            f"/api/v1/businesses/{business_id}/products", headers=outsider_headers
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/api/v1/businesses/{business_id}/products/{product['id']}",
            headers=outsider_headers,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/businesses/{business_id}/products",
            headers=outsider_headers,
            json=product_payload("OUTSIDE"),
        ).status_code
        == 404
    )


def test_member_can_read_but_cannot_write(client: TestClient, db: Session) -> None:
    owner_headers = register_and_login(client, "owner@example.com")
    member_headers = register_and_login(client, "member@example.com")
    business_id = create_business(client, owner_headers)
    client.post(
        f"/api/v1/businesses/{business_id}/products",
        headers=owner_headers,
        json=product_payload(),
    )
    member = db.scalar(select(User).where(User.email == "member@example.com"))
    assert member is not None
    db.add(
        BusinessMember(
            user_id=member.id,
            business_id=UUID(business_id),
            role=BusinessRole.MEMBER,
        )
    )
    db.commit()

    listed = client.get(f"/api/v1/businesses/{business_id}/products", headers=member_headers)
    created = client.post(
        f"/api/v1/businesses/{business_id}/products",
        headers=member_headers,
        json=product_payload("MEMBER"),
    )

    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert created.status_code == 403
