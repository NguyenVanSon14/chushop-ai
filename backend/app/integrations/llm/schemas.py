from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)


AVAILABLE_TOOLS = [
    ToolDefinition(
        name="get_profit_summary",
        description="Lấy tổng quan lợi nhuận ròng, doanh thu, giá vốn, chi phí và biên lợi nhuận của doanh nghiệp.",
    ),
    ToolDefinition(
        name="get_top_products",
        description="Lấy danh sách sản phẩm mang lại lợi nhuận gộp cao nhất.",
    ),
    ToolDefinition(
        name="get_loss_making_products",
        description="Lấy danh sách các sản phẩm đang bán lỗ (lợi nhuận gộp âm).",
    ),
    ToolDefinition(
        name="get_expense_breakdown",
        description="Lấy chi tiết chi phí lớn nhất và phân loại chi phí.",
    ),
    ToolDefinition(
        name="explain_profit_change",
        description="Phân tích lý do lợi nhuận giảm hoặc tăng so với kỳ trước.",
    ),
    ToolDefinition(
        name="compare_channels",
        description="So sánh hiệu quả và lợi nhuận đóng góp giữa các kênh bán (Shopee, TikTok, Cửa hàng...).",
    ),
]


@dataclass
class LLMResponse:
    content: str
    tool_name: str | None = None
    tool_result: dict[str, Any] | None = None
