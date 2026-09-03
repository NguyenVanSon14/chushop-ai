from typing import Any, Protocol

from app.modules.assistant.tools import AssistantIntent, ToolOutput


class ExplanationProvider(Protocol):
    """Boundary for an LLM that may explain only approved structured tool output."""

    def explain(self, output: ToolOutput) -> str: ...


def format_money(value: int) -> str:
    return f"{value:,}".replace(",", ".") + " VND"


def format_period(result: dict[str, Any]) -> str:
    period = result["period"]
    return f"từ {period['date_from']} đến {period['date_to']}"


class DeterministicExplanationProvider:
    """Safe local provider used until an external LLM provider is configured."""

    def explain(self, output: ToolOutput) -> str:
        result = output.result
        period = format_period(result)
        intent = AssistantIntent(output.name)
        if intent == AssistantIntent.UNSUPPORTED:
            return (
                "Money Brain v0.1 chưa đưa ra chiến lược hoặc khuyến nghị tăng trưởng. "
                "Bạn có thể hỏi về lợi nhuận, doanh thu trong kỳ, sản phẩm, chi phí "
                "hoặc hiệu quả kênh bán."
            )
        if intent == AssistantIntent.REVENUE_HEALTH:
            return self._explain_revenue(result, period)
        if intent == AssistantIntent.TOP_PRODUCT:
            product = result["product"]
            if product is None:
                return f"Chưa có dữ liệu bán hàng {period}, nên chưa tìm được sản phẩm lãi nhất."
            return (
                f"Sản phẩm lãi gộp nhiều nhất {period} là {product['name']} "
                f"({product['sku'] or 'không SKU'}), với {format_money(product['gross_profit'])}."
            )
        if intent == AssistantIntent.LOSS_PRODUCTS:
            products = result["products"]
            if not products:
                return f"Không có sản phẩm nào có lợi nhuận gộp âm {period}."
            details = ", ".join(
                f"{product['name']} ({format_money(product['gross_profit'])})"
                for product in products
            )
            return f"Các sản phẩm đang bán lỗ {period}: {details}."
        if intent == AssistantIntent.TOP_EXPENSE:
            expense = result["expense"]
            if expense is None:
                return f"Chưa có chi phí nào được ghi nhận {period}."
            return (
                f"Chi phí lớn nhất {period} là “{expense['description']}” "
                f"({expense['category']}), trị giá {format_money(expense['amount'])}."
            )
        if intent == AssistantIntent.PROFIT_DECLINE:
            return self._explain_profit_change(result, period)
        if intent == AssistantIntent.CHANNELS:
            channels = result["channels"]
            if not channels:
                return f"Chưa có dữ liệu kênh bán hàng {period}."
            leader = channels[0]
            return (
                f"Kênh có lợi nhuận đóng góp cao nhất {period} là {leader['channel']}, "
                f"đạt {format_money(leader['contribution_profit'])}. "
                "Chỉ số này đã trừ giá vốn và phí bán hàng, chưa phân bổ chi phí vận hành."
            )
        summary = result["summary"]
        comparison = result["net_profit_comparison"]
        direction = "tăng" if comparison["difference"] >= 0 else "giảm"
        return (
            f"Lợi nhuận ròng {period} là {format_money(summary['net_profit'])}, "
            f"từ doanh thu {format_money(summary['revenue'])}. "
            f"So với kỳ trước, lợi nhuận {direction} "
            f"{format_money(abs(comparison['difference']))}."
        )

    @staticmethod
    def _explain_profit_change(result: dict[str, Any], period: str) -> str:
        current = result["current"]
        previous = result["previous"]
        net_difference = current["net_profit"] - previous["net_profit"]
        if net_difference >= 0:
            return (
                f"Lợi nhuận ròng {period} không giảm; đã tăng "
                f"{format_money(net_difference)} so với kỳ trước."
            )
        drivers = [
            (previous["revenue"] - current["revenue"], "doanh thu giảm"),
            (current["cogs"] - previous["cogs"], "giá vốn tăng"),
            (current["fees"] - previous["fees"], "phí bán hàng tăng"),
            (current["expenses"] - previous["expenses"], "chi phí vận hành tăng"),
        ]
        negative_drivers = sorted(
            ((impact, label) for impact, label in drivers if impact > 0), reverse=True
        )
        explanation = ", ".join(
            f"{label} {format_money(impact)}" for impact, label in negative_drivers[:3]
        )
        if not explanation:
            explanation = "cơ cấu doanh thu và chi phí thay đổi"
        return (
            f"Lợi nhuận ròng {period} giảm {format_money(abs(net_difference))}. "
            f"Các yếu tố bất lợi chính: {explanation}."
        )

    @staticmethod
    def _explain_revenue(result: dict[str, Any], period: str) -> str:
        revenue = result["revenue"]
        comparison = result["comparison"]
        if revenue == 0:
            return (
                f"Doanh thu {period} đang là 0 VND và chưa có đơn hàng. "
                "Hãy kiểm tra xem dữ liệu bán hàng của kỳ này đã được nhập đầy đủ chưa."
            )
        if comparison["previous"] == 0:
            return (
                f"Doanh thu {period} là {format_money(revenue)} từ "
                f"{result['order_count']} đơn. Kỳ trước chưa có doanh thu nên chưa đủ cơ sở "
                "để đánh giá xu hướng."
            )
        direction = "tăng" if comparison["difference"] >= 0 else "giảm"
        return (
            f"Doanh thu {period} là {format_money(revenue)} từ {result['order_count']} đơn, "
            f"{direction} {format_money(abs(comparison['difference']))} so với kỳ trước."
        )
