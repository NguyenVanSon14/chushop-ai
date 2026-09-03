from fastapi.testclient import TestClient

from tests.conftest import register_and_login
from tests.test_analytics import add_expense
from tests.test_sales import csv_content, setup_business_and_product, upload


def create_conversation(client: TestClient, business_id: str, headers: dict[str, str]) -> str:
    response = client.post(
        f"/api/v1/businesses/{business_id}/assistant/conversations",
        headers=headers,
        json={"title": "Cuộc trò chuyện mới"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def ask(
    client: TestClient,
    business_id: str,
    conversation_id: str,
    headers: dict[str, str],
    question: str,
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/businesses/{business_id}/assistant/conversations/{conversation_id}/messages",
        headers=headers,
        json={
            "question": question,
            "date_from": "2026-09-01",
            "date_to": "2026-09-02",
        },
    )
    assert response.status_code == 200
    return response.json()["assistant_message"]


def setup_money_data(client: TestClient) -> tuple[dict[str, str], str]:
    headers, business_id, _ = setup_business_and_product(client)
    upload(
        client,
        f"/api/v1/businesses/{business_id}/sales/imports",
        headers,
        csv_content(),
    )
    add_expense(
        client,
        business_id=business_id,
        headers=headers,
        amount=100000,
        incurred_on="2026-09-01",
    )
    return headers, business_id


def test_assistant_answers_with_authoritative_tools_and_persists_history(
    client: TestClient,
) -> None:
    headers, business_id = setup_money_data(client)
    conversation_id = create_conversation(client, business_id, headers)

    profit = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Tháng này tôi lời bao nhiêu?",
    )
    assert profit["tool_name"] == "financial_summary"
    assert profit["tool_result"]["summary"]["net_profit"] == 423000
    assert "423.000 VND" in profit["content"]

    product = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Sản phẩm nào lời nhiều nhất?",
    )
    assert product["tool_name"] == "top_product"
    assert product["tool_result"]["product"]["sku"] == "SP-001"

    expense = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Chi phí nào lớn nhất?",
    )
    assert expense["tool_name"] == "top_expense"
    assert expense["tool_result"]["expense"]["amount"] == 100000

    history = client.get(
        f"/api/v1/businesses/{business_id}/assistant/conversations/{conversation_id}",
        headers=headers,
    )
    assert history.status_code == 200
    assert len(history.json()["messages"]) == 6
    assert history.json()["title"] == "Tháng này tôi lời bao nhiêu?"


def test_assistant_supports_loss_decline_and_channel_tools(client: TestClient) -> None:
    headers, business_id = setup_money_data(client)
    conversation_id = create_conversation(client, business_id, headers)
    previous_csv = (
        b"order_code,channel,ordered_at,sku,quantity,unit_price,fees\n"
        b"DH-PREV-AI,SHOPEE,2026-08-31T10:00:00+07:00,SP-001,1,1000000,5000\n"
    )
    upload(
        client,
        f"/api/v1/businesses/{business_id}/sales/imports",
        headers,
        previous_csv,
    )

    loss = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Sản phẩm nào đang bán lỗ?",
    )
    decline = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Tại sao lợi nhuận tuần này giảm?",
    )
    channel = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Shopee hay TikTok mang lại lợi nhuận cao hơn?",
    )

    assert loss["tool_name"] == "loss_products"
    assert loss["tool_result"]["products"] == []
    assert decline["tool_name"] == "profit_decline"
    assert decline["tool_result"]["current"]["net_profit"] == 423000
    assert decline["tool_result"]["previous"]["net_profit"] == 875000
    assert "giảm 452.000 VND" in decline["content"]
    assert channel["tool_name"] == "channel_profitability"
    assert channel["tool_result"]["channels"][0]["channel"] == "SHOPEE"


def test_assistant_conversations_are_tenant_isolated(client: TestClient) -> None:
    headers, business_id = setup_money_data(client)
    conversation_id = create_conversation(client, business_id, headers)
    outsider_headers = register_and_login(client, "assistant-outsider@example.com")

    assert (
        client.get(
            f"/api/v1/businesses/{business_id}/assistant/conversations",
            headers=outsider_headers,
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/businesses/{business_id}/assistant/conversations/{conversation_id}/messages",
            headers=outsider_headers,
            json={"question": "Tôi lời bao nhiêu?"},
        ).status_code
        == 404
    )


def test_assistant_validates_period_and_unknown_conversation(client: TestClient) -> None:
    headers, business_id = setup_money_data(client)
    conversation_id = create_conversation(client, business_id, headers)

    incomplete_period = client.post(
        f"/api/v1/businesses/{business_id}/assistant/conversations/{conversation_id}/messages",
        headers=headers,
        json={"question": "Tôi lời bao nhiêu?", "date_from": "2026-09-01"},
    )
    missing = client.get(
        f"/api/v1/businesses/{business_id}/assistant/conversations/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )

    assert incomplete_period.status_code == 422
    assert missing.status_code == 404


def test_assistant_does_not_force_unknown_questions_into_profit_summary(
    client: TestClient,
) -> None:
    headers = register_and_login(client)
    business_id = client.post(
        "/api/v1/businesses", headers=headers, json={"name": "Shop Doanh Thu"}
    ).json()["id"]
    conversation_id = create_conversation(client, business_id, headers)

    revenue = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Bạn hãy xem thử mức doanh thu vậy ổn không",
    )
    recommendation = ask(
        client,
        business_id,
        conversation_id,
        headers,
        "Phải làm sao doanh thu mới tăng lên",
    )

    assert revenue["tool_name"] == "revenue_health"
    assert "Doanh thu" in revenue["content"]
    assert "0 VND" in revenue["content"]
    assert recommendation["tool_name"] == "unsupported_question"
    assert "chưa đưa ra chiến lược" in recommendation["content"]


def test_real_llm_provider_tool_selection_and_explanation(monkeypatch) -> None:
    from app.integrations.llm.client import RealLLMProvider
    from app.modules.assistant.tools import AssistantIntent, ToolOutput

    provider = RealLLMProvider(api_key="test-key", model="gpt-4o-mini")

    def mock_post(self, url, headers=None, json=None):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                # If it's tool selection prompt
                messages = json.get("messages", [])
                if any("Nhiệm vụ của bạn là chọn đúng" in m.get("content", "") for m in messages):
                    return {
                        "choices": [
                            {
                                "message": {
                                    "tool_calls": [
                                        {"function": {"name": "get_profit_summary"}}
                                    ]
                                }
                            }
                        ]
                    }
                # Explanation prompt
                return {
                    "choices": [
                        {
                            "message": {
                                "content": "Tháng này shop đạt 423.000 VND lợi nhuận ròng."
                            }
                        }
                    ]
                }

        return MockResponse()

    monkeypatch.setattr("httpx.Client.post", mock_post)

    def execute_tool(intent: AssistantIntent) -> ToolOutput:
        assert intent == AssistantIntent.SUMMARY
        return ToolOutput(
            name=intent.value,
            result={"summary": {"net_profit": 423000, "revenue": 908000}},
        )

    output, explanation = provider.process_question("Tháng này tôi lời bao nhiêu?", execute_tool)
    assert output.name == "financial_summary"
    assert explanation == "Tháng này shop đạt 423.000 VND lợi nhuận ròng."


def test_real_llm_provider_handles_missing_key_and_network_error(monkeypatch) -> None:
    from app.integrations.llm.client import RealLLMProvider
    from app.modules.assistant.tools import AssistantIntent, ToolOutput

    # Missing API Key fallback
    no_key_provider = RealLLMProvider(api_key="", model="gpt-4o-mini")

    def execute_tool(intent: AssistantIntent) -> ToolOutput:
        return ToolOutput(
            name=intent.value,
            result={
                "summary": {"net_profit": 100000, "revenue": 500000},
                "period": {"date_from": "2026-09-01", "date_to": "2026-09-03"},
                "net_profit_comparison": {"difference": 0},
            },
        )

    output, explanation = no_key_provider.process_question("Tháng này tôi lời bao nhiêu?", execute_tool)
    assert output.name == "financial_summary"
    assert "100.000 VND" in explanation

    # Provider Error fallback
    error_provider = RealLLMProvider(api_key="bad-key", model="gpt-4o-mini")

    def mock_post_error(self, url, headers=None, json=None):
        raise Exception("API Connection error")

    monkeypatch.setattr("httpx.Client.post", mock_post_error)

    output, explanation = error_provider.process_question("Tháng này tôi lời bao nhiêu?", execute_tool)
    assert output.name == "financial_summary"
    assert "100.000 VND" in explanation


def test_all_6_mvp_questions_supported(client: TestClient) -> None:
    headers, business_id = setup_money_data(client)
    conversation_id = create_conversation(client, business_id, headers)

    questions = [
        ("Tháng này tôi lời bao nhiêu?", "financial_summary"),
        ("Sản phẩm nào lời nhiều nhất?", "top_product"),
        ("Sản phẩm nào đang bán lỗ?", "loss_products"),
        ("Chi phí nào lớn nhất?", "top_expense"),
        ("Tại sao lợi nhuận tuần này giảm?", "profit_decline"),
        ("Shopee hay TikTok mang lại lợi nhuận cao hơn?", "channel_profitability"),
    ]

    for question, expected_tool in questions:
        reply = ask(client, business_id, conversation_id, headers, question)
        assert reply["tool_name"] == expected_tool, f"Failed for question: {question}"
        assert reply["content"] is not None and len(reply["content"]) > 0

