from fastapi.testclient import TestClient

from tests.conftest import register_and_login


def create_business(client: TestClient, headers: dict[str, str]) -> str:
    return client.post("/api/v1/businesses", headers=headers, json={"name": "Shop Chi Phí"}).json()[
        "id"
    ]


def test_expense_crud_and_integer_validation(client: TestClient) -> None:
    headers = register_and_login(client)
    business_id = create_business(client, headers)
    payload = {
        "description": "Quảng cáo tháng 9",
        "category": "MARKETING",
        "amount": 500000,
        "incurred_on": "2026-09-03",
    }

    created = client.post(
        f"/api/v1/businesses/{business_id}/expenses", headers=headers, json=payload
    )
    assert created.status_code == 201
    expense_id = created.json()["id"]

    listed = client.get(f"/api/v1/businesses/{business_id}/expenses", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["amount"] == 500000

    updated = client.patch(
        f"/api/v1/businesses/{business_id}/expenses/{expense_id}",
        headers=headers,
        json={"amount": 600000},
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == 600000

    invalid = client.post(
        f"/api/v1/businesses/{business_id}/expenses",
        headers=headers,
        json={**payload, "amount": 1.5},
    )
    assert invalid.status_code == 422

    deleted = client.delete(
        f"/api/v1/businesses/{business_id}/expenses/{expense_id}", headers=headers
    )
    assert deleted.status_code == 204


def test_expenses_are_tenant_isolated(client: TestClient) -> None:
    owner_headers = register_and_login(client, "owner@example.com")
    outsider_headers = register_and_login(client, "outsider@example.com")
    business_id = create_business(client, owner_headers)

    assert (
        client.get(
            f"/api/v1/businesses/{business_id}/expenses", headers=outsider_headers
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/businesses/{business_id}/expenses",
            headers=outsider_headers,
            json={
                "description": "Sai tenant",
                "category": "OTHER",
                "amount": 1000,
                "incurred_on": "2026-09-03",
            },
        ).status_code
        == 404
    )
