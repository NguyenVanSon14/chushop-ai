from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook

from tests.conftest import register_and_login


def setup_business_and_product(
    client: TestClient, email: str = "owner@example.com"
) -> tuple[dict[str, str], str, str]:
    headers = register_and_login(client, email)
    business = client.post(
        "/api/v1/businesses", headers=headers, json={"name": f"Shop {email}"}
    ).json()
    product = client.post(
        f"/api/v1/businesses/{business['id']}/products",
        headers=headers,
        json={
            "name": "Áo thun",
            "sku": "SP-001",
            "selling_price": 299000,
            "cost_price": 120000,
            "is_active": True,
        },
    ).json()
    return headers, business["id"], product["id"]


def csv_content() -> bytes:
    return (
        b"order_code,channel,ordered_at,sku,quantity,unit_price,fees\n"
        b"DH-001,SHOPEE,2026-09-01T10:00:00+07:00,SP-001,2,299000,15000\n"
        b"DH-002,TIKTOK,2026-09-02T11:00:00+07:00,SP-001,1,310000,10000\n"
    )


def upload(client: TestClient, path: str, headers: dict[str, str], content: bytes | None = None):
    return client.post(
        path,
        headers=headers,
        files={"file": ("sales.csv", content or csv_content(), "text/csv")},
    )


def test_preview_calculates_integer_totals(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)

    response = upload(client, f"/api/v1/businesses/{business_id}/sales/imports/preview", headers)

    assert response.status_code == 200
    assert response.json()["row_count"] == 2
    assert response.json()["order_count"] == 2
    assert response.json()["total_revenue"] == 908000
    assert response.json()["total_cost"] == 360000
    assert response.json()["total_fees"] == 25000


def test_import_snapshots_cost_and_rejects_duplicate(client: TestClient) -> None:
    headers, business_id, product_id = setup_business_and_product(client)
    path = f"/api/v1/businesses/{business_id}/sales/imports"

    imported = upload(client, path, headers)
    duplicate = upload(client, path, headers)
    client.patch(
        f"/api/v1/businesses/{business_id}/products/{product_id}",
        headers=headers,
        json={"cost_price": 200000},
    )
    orders = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=headers)

    assert imported.status_code == 201
    assert duplicate.status_code == 409
    assert orders.status_code == 200
    first_item = next(
        item
        for order in orders.json()
        for item in order["items"]
        if order["external_id"] == "DH-001"
    )
    assert first_item["cost_price_snapshot"] == 120000


def test_unknown_sku_is_rejected(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)
    content = csv_content().replace(b"SP-001", b"UNKNOWN")

    response = upload(
        client,
        f"/api/v1/businesses/{business_id}/sales/imports/preview",
        headers,
        content,
    )

    assert response.status_code == 422
    assert "UNKNOWN" in response.json()["detail"]


def test_sales_are_tenant_isolated(client: TestClient) -> None:
    owner_headers, business_id, _ = setup_business_and_product(client)
    outsider_headers = register_and_login(client, "outsider@example.com")

    preview = upload(
        client,
        f"/api/v1/businesses/{business_id}/sales/imports/preview",
        outsider_headers,
    )
    orders = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=outsider_headers)

    assert preview.status_code == 404
    assert orders.status_code == 404


def test_xlsx_preview(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["order_code", "channel", "ordered_at", "sku", "quantity", "unit_price", "fees"])
    sheet.append(["DH-XLSX", "SHOPEE", "2026-09-01T10:00:00+07:00", "SP-001", 1, 299000, 5000])
    output = BytesIO()
    workbook.save(output)

    response = client.post(
        f"/api/v1/businesses/{business_id}/sales/imports/preview",
        headers=headers,
        files={
            "file": (
                "sales.xlsx",
                output.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["order_count"] == 1


def test_create_manual_order_calculates_money_and_snapshots_cost(client: TestClient) -> None:
    headers, business_id, product_id = setup_business_and_product(client)
    payload = {
        "order_code": "THU-CONG-001",
        "channel": "cửa hàng",
        "ordered_at": "2026-09-03T14:30:00",
        "fees": 5000,
        "items": [{"product_id": product_id, "quantity": 2, "unit_price": 280000}],
    }

    created = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders",
        headers=headers,
        json=payload,
    )
    client.patch(
        f"/api/v1/businesses/{business_id}/products/{product_id}",
        headers=headers,
        json={"cost_price": 200000},
    )
    listed = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=headers)

    assert created.status_code == 201
    assert created.json()["channel"] == "CỬA HÀNG"
    assert created.json()["revenue"] == 560000
    assert created.json()["cogs"] == 240000
    assert created.json()["items"][0]["cost_price_snapshot"] == 120000
    assert listed.json()[0]["items"][0]["cost_price_snapshot"] == 120000


def test_manual_order_validates_integer_money_and_duplicate_code(client: TestClient) -> None:
    headers, business_id, product_id = setup_business_and_product(client)
    payload = {
        "order_code": "MANUAL-DUPLICATE",
        "channel": "STORE",
        "ordered_at": "2026-09-03T14:30:00+07:00",
        "fees": 0,
        "items": [{"product_id": product_id, "quantity": 1, "unit_price": 299000}],
    }

    first = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders", headers=headers, json=payload
    )
    duplicate = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders", headers=headers, json=payload
    )
    invalid_money = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders",
        headers=headers,
        json={**payload, "order_code": "FLOAT", "fees": 1.5},
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert invalid_money.status_code == 422


def test_manual_order_rejects_cross_tenant_product_and_access(client: TestClient) -> None:
    owner_headers, business_id, _ = setup_business_and_product(client)
    outsider_headers, outsider_business_id, outsider_product_id = setup_business_and_product(
        client, "manual-outsider@example.com"
    )
    payload = {
        "channel": "STORE",
        "ordered_at": "2026-09-03T14:30:00+07:00",
        "fees": 0,
        "items": [{"product_id": outsider_product_id, "quantity": 1, "unit_price": 299000}],
    }

    foreign_product = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders",
        headers=owner_headers,
        json=payload,
    )
    foreign_business = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders",
        headers=outsider_headers,
        json={
            **payload,
            "items": [{"product_id": outsider_product_id, "quantity": 1, "unit_price": 299000}],
        },
    )

    assert outsider_business_id != business_id
    assert foreign_product.status_code == 422
    assert foreign_business.status_code == 404


def test_delete_manual_order_removes_order_and_items(client: TestClient) -> None:
    headers, business_id, product_id = setup_business_and_product(client)
    payload = {
        "order_code": "DELETE-ME",
        "channel": "STORE",
        "ordered_at": "2026-09-03T14:30:00+07:00",
        "fees": 5000,
        "items": [{"product_id": product_id, "quantity": 2, "unit_price": 280000}],
    }

    created = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders", headers=headers, json=payload
    )
    order_id = created.json()["id"]

    deleted = client.delete(
        f"/api/v1/businesses/{business_id}/sales/orders/{order_id}", headers=headers
    )
    listed = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=headers)

    assert created.status_code == 201
    assert deleted.status_code == 204
    assert len(listed.json()) == 0


def test_delete_order_returns_404_for_unknown_id(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/api/v1/businesses/{business_id}/sales/orders/{fake_id}", headers=headers
    )

    assert response.status_code == 404


def test_delete_order_is_tenant_isolated(client: TestClient) -> None:
    owner_headers, business_id, product_id = setup_business_and_product(client)
    outsider_headers = register_and_login(client, "delete-outsider@example.com")

    created = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders",
        headers=owner_headers,
        json={
            "channel": "STORE",
            "ordered_at": "2026-09-03T14:30:00+07:00",
            "fees": 0,
            "items": [{"product_id": product_id, "quantity": 1, "unit_price": 299000}],
        },
    )
    order_id = created.json()["id"]

    outsider_delete = client.delete(
        f"/api/v1/businesses/{business_id}/sales/orders/{order_id}",
        headers=outsider_headers,
    )
    owner_list = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=owner_headers)

    assert outsider_delete.status_code == 404
    assert len(owner_list.json()) == 1


def test_delete_import_removes_all_associated_orders(client: TestClient) -> None:
    headers, business_id, _ = setup_business_and_product(client)
    path = f"/api/v1/businesses/{business_id}/sales/imports"

    imported = upload(client, path, headers)
    import_id = imported.json()["id"]
    orders_before = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=headers)

    deleted = client.delete(
        f"/api/v1/businesses/{business_id}/sales/imports/{import_id}", headers=headers
    )
    orders_after = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=headers)

    assert imported.status_code == 201
    assert len(orders_before.json()) == 2
    assert deleted.status_code == 204
    assert len(orders_after.json()) == 0


def test_delete_import_is_tenant_isolated(client: TestClient) -> None:
    owner_headers, business_id, _ = setup_business_and_product(client)
    outsider_headers = register_and_login(client, "import-outsider@example.com")
    path = f"/api/v1/businesses/{business_id}/sales/imports"

    imported = upload(client, path, owner_headers)
    import_id = imported.json()["id"]

    outsider_delete = client.delete(
        f"/api/v1/businesses/{business_id}/sales/imports/{import_id}",
        headers=outsider_headers,
    )
    orders = client.get(f"/api/v1/businesses/{business_id}/sales/orders", headers=owner_headers)

    assert outsider_delete.status_code == 404
    assert len(orders.json()) == 2


def test_analytics_updates_after_order_deletion(client: TestClient) -> None:
    headers, business_id, product_id = setup_business_and_product(client)
    payload = {
        "channel": "STORE",
        "ordered_at": "2026-09-01T10:00:00+07:00",
        "fees": 5000,
        "items": [{"product_id": product_id, "quantity": 2, "unit_price": 280000}],
    }
    created = client.post(
        f"/api/v1/businesses/{business_id}/sales/orders", headers=headers, json=payload
    )
    order_id = created.json()["id"]

    analytics_before = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2026-09-01", "date_to": "2026-09-30"},
    )

    client.delete(f"/api/v1/businesses/{business_id}/sales/orders/{order_id}", headers=headers)

    analytics_after = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2026-09-01", "date_to": "2026-09-30"},
    )

    assert analytics_before.json()["summary"]["revenue"] == 560000
    assert analytics_after.json()["summary"]["revenue"] == 0
    assert analytics_after.json()["summary"]["order_count"] == 0
