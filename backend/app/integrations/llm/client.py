import json
import logging
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.modules.assistant.provider import DeterministicExplanationProvider
from app.modules.assistant.tools import AssistantIntent, ToolOutput, classify_intent

logger = logging.getLogger(__name__)

# Map external tool names to AssistantIntent
TOOL_NAME_TO_INTENT: dict[str, AssistantIntent] = {
    "get_profit_summary": AssistantIntent.SUMMARY,
    "financial_summary": AssistantIntent.SUMMARY,
    "get_revenue_health": AssistantIntent.REVENUE_HEALTH,
    "revenue_health": AssistantIntent.REVENUE_HEALTH,
    "get_top_products": AssistantIntent.TOP_PRODUCT,
    "top_product": AssistantIntent.TOP_PRODUCT,
    "get_loss_making_products": AssistantIntent.LOSS_PRODUCTS,
    "loss_products": AssistantIntent.LOSS_PRODUCTS,
    "get_expense_breakdown": AssistantIntent.TOP_EXPENSE,
    "top_expense": AssistantIntent.TOP_EXPENSE,
    "explain_profit_change": AssistantIntent.PROFIT_DECLINE,
    "profit_decline": AssistantIntent.PROFIT_DECLINE,
    "compare_channels": AssistantIntent.CHANNELS,
    "channel_profitability": AssistantIntent.CHANNELS,
}

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_profit_summary",
            "description": "Lấy tổng quan lợi nhuận ròng, doanh thu, giá vốn và chi phí.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_revenue_health",
            "description": "Đánh giá sức khỏe doanh thu và số lượng đơn hàng.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_products",
            "description": "Lấy sản phẩm mang lại lợi nhuận gộp nhiều nhất.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_loss_making_products",
            "description": "Lấy danh sách các sản phẩm đang bán lỗ (lợi nhuận gộp âm).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_breakdown",
            "description": "Lấy chi phí vận hành lớn nhất.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_profit_change",
            "description": (
                "Phân tích nguyên nhân lợi nhuận sụt giảm hoặc thay đổi so với kỳ trước."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_channels",
            "description": "So sánh lợi nhuận giữa các kênh bán (Shopee, TikTok, Cửa hàng...).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


class MockLLMProvider:
    """Deterministic local provider used in automated tests and offline mode."""

    def __init__(self) -> None:
        self.deterministic = DeterministicExplanationProvider()

    def process_question(
        self,
        question: str,
        execute_tool_fn: Any,
    ) -> tuple[ToolOutput, str]:
        intent = classify_intent(question)
        output: ToolOutput = execute_tool_fn(intent)
        explanation = self.deterministic.explain(output)
        return output, explanation


class RealLLMProvider:
    """Real LLM Provider supporting OpenAI / Gemini / Groq OpenAI-compatible APIs."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.fallback = MockLLMProvider()

    def process_question(
        self,
        question: str,
        execute_tool_fn: Any,
    ) -> tuple[ToolOutput, str]:
        if not self.api_key:
            logger.warning("LLM_API_KEY missing, using mock fallback")
            return self.fallback.process_question(question, execute_tool_fn)

        try:
            # 1. Ask LLM which tool to execute
            intent, tool_name = self._select_tool(question)
            output: ToolOutput = execute_tool_fn(intent)

            # If unsupported, return early with clear explanation
            if intent == AssistantIntent.UNSUPPORTED:
                explanation = self.fallback.deterministic.explain(output)
                return output, explanation

            # Ask the LLM to explain the authoritative Python Money Brain result.
            explanation = self._generate_explanation(question, output)
            return output, explanation

        except Exception as err:
            logger.error("LLM Provider error: %s. Falling back to deterministic provider.", err)
            # Fall back safely without crashing
            return self.fallback.process_question(question, execute_tool_fn)

    def _select_tool(self, question: str) -> tuple[AssistantIntent, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Bạn là Trợ lý tài chính ChủShop AI. Nhiệm vụ của bạn là chọn "
                        "đúng duy nhất "
                        "1 tool phù hợp để tra cứu số liệu tài chính theo câu hỏi của chủ shop. "
                        "Nếu câu hỏi yêu cầu tư vấn chiến lược/mẹo kinh doanh không có trong tool, "
                        "không chọn tool nào."
                    ),
                },
                {"role": "user", "content": question},
            ],
            "tools": OPENAI_TOOLS,
            "tool_choice": "auto",
            "temperature": 0.0,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()

        message = data["choices"][0]["message"]
        tool_calls = message.get("tool_calls")
        if tool_calls and len(tool_calls) > 0:
            fn_name = tool_calls[0]["function"]["name"]
            intent = TOOL_NAME_TO_INTENT.get(fn_name, AssistantIntent.UNSUPPORTED)
            return intent, fn_name

        # Fallback to local classification if LLM didn't emit a tool_call
        fallback_intent = classify_intent(question)
        return fallback_intent, fallback_intent.value

    def _generate_explanation(self, question: str, output: ToolOutput) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        system_prompt = (
            "Bạn là Trợ lý tài chính ChủShop AI. Hãy đọc kết quả tính toán chính xác từ hệ thống "
            "Python Money Brain bên dưới và trả lời câu hỏi của chủ shop bằng tiếng Việt ngắn gọn, "
            "dễ hiểu, thân thiện.\n"
            "QUY TẮC BẮT BUỘC:\n"
            "1. Tuyệt đối KHÔNG tự tính toán hay sửa đổi các số liệu trong kết quả.\n"
            "2. Tuyệt đối KHÔNG đưa thêm bất kỳ số liệu nào không có trong dữ liệu được cung cấp.\n"
            "3. Nếu dữ liệu báo chưa có hoặc trống, phải nói rõ là chưa có đủ dữ liệu."
        )

        user_prompt = (
            f'Câu hỏi của chủ shop: "{question}"\n'
            f"Tên tool: {output.name}\n"
            f"Kết quả số liệu từ Money Brain (JSON):\n"
            f"{json.dumps(output.result, ensure_ascii=False)}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions", headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return content.strip() if content else self.fallback.deterministic.explain(output)


def get_llm_provider(settings: Settings | None = None) -> MockLLMProvider | RealLLMProvider:
    if settings is None:
        settings = get_settings()

    provider_name = (settings.llm_provider or "mock").lower().strip()
    if provider_name != "mock" and settings.llm_api_key:
        return RealLLMProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    return MockLLMProvider()
