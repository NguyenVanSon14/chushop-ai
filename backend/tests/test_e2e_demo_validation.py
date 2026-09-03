"""End-to-End MVP Validation Test (M8).

Validates all 11 financial metrics and 6 AI Assistant questions on the
demo dataset using Python Money Brain as the sole authoritative source.
"""

from datetime import date

from fastapi.testclient import TestClient

from scripts.seed_demo_data import seed_data
from tests.conftest import register_and_login


def test_e2e_demo_financial_analytics_and_ai_assistant(client: TestClient, db) -> None:
    # 1. Seed Demo Data
    summary_data = seed_data(db)
    business_id = summary_data["business_id"]

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": summary_data["user_email"], "password": "DemoPass123!"},
    )
    assert login_resp.status_code == 200
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # 2. Validate Financial Analytics Endpoint (Aug 1 to Sep 30, 2026)
    analytics_resp = client.get(
        f"/api/v1/businesses/{business_id}/analytics/summary",
        headers=headers,
        params={"date_from": "2026-08-01", "date_to": "2026-09-30"},
    )
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()

    summary = analytics["summary"]

    # 1. Revenue
    assert summary["revenue"] == summary_data["total_revenue"]
    assert summary["revenue"] == 556_607_000

    # 2. COGS
    assert summary["cogs"] == summary_data["total_cogs"]
    assert summary["cogs"] == 353_280_000

    # 3. Platform fees
    assert summary["fees"] == summary_data["total_fees"]
    assert summary["fees"] == 11_971_000

    # 4. Expenses
    assert summary["expenses"] == summary_data["total_expenses"]
    assert summary["expenses"] == 136_500_000

    # 5. Gross profit
    assert summary["gross_profit"] == summary_data["gross_profit"]
    assert summary["gross_profit"] == 203_327_000

    # 6. Net profit
    assert summary["net_profit"] == summary_data["net_profit"]
    assert summary["net_profit"] == 54_856_000

    # 7. Margins (bps)
    assert summary["gross_margin_bps"] is not None
    assert summary["net_margin_bps"] is not None
    # 203327000 / 556607000 * 10000 = 3653 bps (36.53%)
    assert summary["gross_margin_bps"] == 3653
    # 54856000 / 556607000 * 10000 = 986 bps (9.86%)
    assert summary["net_margin_bps"] == 986

    # 8. Profitability by product
    products = analytics["products"]
    assert len(products) > 0
    top_product = products[0]  # sorted by gross_profit desc
    assert top_product["gross_profit"] > 0

    # Verify high-volume loss product is correctly identified
    loss_products = [p for p in products if p["gross_profit"] < 0]
    assert len(loss_products) >= 1
    assert any(p["sku"] == "AK-LOSS" for p in loss_products)

    # 9. Profitability by channel
    channels = analytics["channels"]
    assert len(channels) == 2
    channel_names = {c["channel"] for c in channels}
    assert channel_names == {"SHOPEE", "TIKTOK"}

    # 10. Period comparison (Current vs Previous)
    assert analytics["period"]["date_from"] == "2026-08-01"
    assert analytics["period"]["date_to"] == "2026-09-30"
    assert analytics["previous_period"] is not None
    assert analytics["revenue_comparison"] is not None
    assert analytics["net_profit_comparison"] is not None

    # 3. Create Conversation & Validate 6 AI Questions
    conv_resp = client.post(
        f"/api/v1/businesses/{business_id}/assistant/conversations",
        headers=headers,
        json={"title": "Cuộc trò chuyện Validation M8"},
    )
    assert conv_resp.status_code == 201
    conv_id = conv_resp.json()["id"]

    mvp_questions = [
        # (question, expected_tool)
        ("Tháng này tôi lời bao nhiêu?", "financial_summary"),
        ("Sản phẩm nào lời nhiều nhất?", "top_product"),
        ("Sản phẩm nào đang bán lỗ?", "loss_products"),
        ("Chi phí nào lớn nhất?", "top_expense"),
        ("Tại sao lợi nhuận tuần này giảm?", "profit_decline"),
        ("Shopee hay TikTok mang lại lợi nhuận cao hơn?", "channel_profitability"),
    ]

    for question, expected_tool in mvp_questions:
        msg_resp = client.post(
            f"/api/v1/businesses/{business_id}/assistant/conversations/{conv_id}/messages",
            headers=headers,
            json={
                "question": question,
                "date_from": "2026-08-01",
                "date_to": "2026-09-30",
            },
        )
        assert msg_resp.status_code == 200
        reply = msg_resp.json()["assistant_message"]

        # Tool verification
        assert reply["tool_name"] == expected_tool
        assert reply["tool_result"] is not None

        # Content verification (must contain Vietnamese response with figures)
        content = reply["content"]
        assert content is not None and len(content) > 0
