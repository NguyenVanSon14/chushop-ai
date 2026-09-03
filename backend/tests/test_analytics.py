from fastapi.testclient import TestClient

from tests.conftest import register_and_login
from tests.test_sales import csv_content, setup_business_and_product, upload


def add_expense(
    client: TestClient,
    *,
    business_id: str,
    headers: dict[str, str],
    amount: int,
    incurred_on: str,
) -> None:
    response = client.post(
        f"/api/v1/businesses/{business_id}/expenses",
        headers=headers,
        json={
            "description": f"Chi phí {incurred_on}",
            "category": "OPERATIONS",
            "amount": amount,
            "incurred_on": incurred_on,
        },
    )
    assert response.status_code == 201


def test_money_brain_summary_and_breakdowns(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)
    upload(
        client,
        f"/api/v1/businesses/{business_id}/sales/imports",
        headers,
        csv_content(),
    )
    previous_csv = (
        b"order_code,channel,ordered_at,sku,quantity,unit_price,fees\n"
        b"DH-PREV,SHOPEE,2026-08-30T10:00:00+07:00,SP-001,1,200000,5000\n"
    )
    upload(
        client,
        f"/api/v1/businesses/{business_id}/sales/imports",
        headers,
        previous_csv,
    )
    add_expense(
        client,
        business_id=business_id,
        headers=headers,
        amount=100000,
        incurred_on="2026-09-01",
    )
    add_expense(
        client,
        business_id=business_id,
        headers=headers,
        amount=20000,
        incurred_on="2026-08-31",
    )

    response = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2026-09-01", "date_to": "2026-09-02"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == {
        "order_count": 2,
        "revenue": 908000,
        "cogs": 360000,
        "fees": 25000,
        "gross_profit": 548000,
        "expenses": 100000,
        "net_profit": 423000,
        "gross_margin_bps": 6035,
        "net_margin_bps": 4659,
    }
    assert data["previous_period"] == {
        "date_from": "2026-08-30",
        "date_to": "2026-08-31",
    }
    assert data["revenue_comparison"] == {
        "current": 908000,
        "previous": 200000,
        "difference": 708000,
        "change_bps": 35400,
    }
    assert data["net_profit_comparison"]["previous"] == 55000
    assert data["products"][0]["quantity"] == 3
    assert data["products"][0]["gross_profit"] == 548000
    assert [channel["channel"] for channel in data["channels"]] == ["SHOPEE", "TIKTOK"]
    assert data["channels"][0]["contribution_profit"] == 343000
    assert data["trends"] == [
        {
            "date": "2026-09-01",
            "revenue": 598000,
            "cogs": 240000,
            "fees": 15000,
            "expenses": 100000,
            "net_profit": 243000,
        },
        {
            "date": "2026-09-02",
            "revenue": 310000,
            "cogs": 120000,
            "fees": 10000,
            "expenses": 0,
            "net_profit": 180000,
        },
    ]


def test_empty_period_has_zeroes_and_null_margins(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)

    response = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2026-01-01", "date_to": "2026-01-01"},
    )

    assert response.status_code == 200
    assert response.json()["summary"]["revenue"] == 0
    assert response.json()["summary"]["gross_margin_bps"] is None
    assert response.json()["revenue_comparison"]["change_bps"] is None


def test_analytics_are_tenant_isolated(client: TestClient) -> None:
    _, business_id, _ = setup_business_and_product(client)
    outsider_headers = register_and_login(client, "outsider@example.com")

    response = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=outsider_headers,
        params={"date_from": "2026-09-01", "date_to": "2026-09-02"},
    )

    assert response.status_code == 404


def test_analytics_reject_invalid_period(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)

    reversed_period = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2026-09-02", "date_to": "2026-09-01"},
    )
    too_long = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2025-01-01", "date_to": "2026-09-01"},
    )

    assert reversed_period.status_code == 422
    assert too_long.status_code == 422
