import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.service import AnalyticsService
from app.modules.businesses.model import Business
from app.modules.users.model import User


class AssistantIntent(StrEnum):
    SUMMARY = "financial_summary"
    REVENUE_HEALTH = "revenue_health"
    TOP_PRODUCT = "top_product"
    LOSS_PRODUCTS = "loss_products"
    TOP_EXPENSE = "top_expense"
    PROFIT_DECLINE = "profit_decline"
    CHANNELS = "channel_profitability"
    UNSUPPORTED = "unsupported_question"


@dataclass(frozen=True)
class ToolOutput:
    name: str
    result: dict[str, Any]


def normalize_question(question: str) -> str:
    normalized = unicodedata.normalize("NFD", question.lower())
    return "".join(character for character in normalized if unicodedata.category(character) != "Mn")


def classify_intent(question: str) -> AssistantIntent:
    value = normalize_question(question)
    if "doanh thu" in value and any(
        phrase in value for phrase in ("lam sao", "cach nao", "nen lam gi", "tang len")
    ):
        return AssistantIntent.UNSUPPORTED
    if "doanh thu" in value and any(
        phrase in value for phrase in ("on khong", "the nao", "bao nhieu", "danh gia")
    ):
        return AssistantIntent.REVENUE_HEALTH
    if "san pham" in value and any(word in value for word in ("ban lo", "dang lo", "bi lo")):
        return AssistantIntent.LOSS_PRODUCTS
    if "san pham" in value and any(word in value for word in ("nhieu nhat", "cao nhat")):
        return AssistantIntent.TOP_PRODUCT
    if "chi phi" in value and any(word in value for word in ("lon nhat", "cao nhat")):
        return AssistantIntent.TOP_EXPENSE
    if "tai sao" in value and "loi nhuan" in value and "giam" in value:
        return AssistantIntent.PROFIT_DECLINE
    if any(word in value for word in ("shopee", "tiktok", "kenh")) and "loi" in value:
        return AssistantIntent.CHANNELS
    if any(
        phrase in value for phrase in ("loi bao nhieu", "lai bao nhieu", "loi nhuan", "tong quan")
    ):
        return AssistantIntent.SUMMARY
    return AssistantIntent.UNSUPPORTED


class AnalyticsToolExecutor:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.analytics_repository = AnalyticsRepository(db)

    def default_period(self, business: Business) -> tuple[date, date]:
        today = datetime.now(UTC).astimezone(ZoneInfo(business.timezone)).date()
        return today.replace(day=1), today

    def execute(
        self,
        *,
        intent: AssistantIntent,
        business: Business,
        user: User,
        date_from: date,
        date_to: date,
    ) -> ToolOutput:
        report = AnalyticsService(self.db).get(
            business_id=business.id,
            date_from=date_from,
            date_to=date_to,
            user=user,
        )
        base = {
            "period": report.period.model_dump(mode="json"),
            "currency": business.currency,
        }
        if intent == AssistantIntent.UNSUPPORTED:
            return ToolOutput(name=intent.value, result=base)
        if intent == AssistantIntent.REVENUE_HEALTH:
            return ToolOutput(
                name=intent.value,
                result={
                    **base,
                    "revenue": report.summary.revenue,
                    "order_count": report.summary.order_count,
                    "comparison": report.revenue_comparison.model_dump(mode="json"),
                },
            )
        if intent == AssistantIntent.TOP_PRODUCT:
            return ToolOutput(
                name=intent.value,
                result={
                    **base,
                    "product": report.products[0].model_dump(mode="json")
                    if report.products
                    else None,
                },
            )
        if intent == AssistantIntent.LOSS_PRODUCTS:
            return ToolOutput(
                name=intent.value,
                result={
                    **base,
                    "products": [
                        product.model_dump(mode="json")
                        for product in report.products
                        if product.gross_profit < 0
                    ],
                },
            )
        if intent == AssistantIntent.TOP_EXPENSE:
            expenses = self.analytics_repository.expenses(
                business_id=business.id, start=date_from, end=date_to
            )
            largest = max(expenses, key=lambda expense: expense.amount, default=None)
            return ToolOutput(
                name=intent.value,
                result={
                    **base,
                    "expense": (
                        {
                            "description": largest.description,
                            "category": largest.category,
                            "amount": largest.amount,
                            "incurred_on": largest.incurred_on.isoformat(),
                        }
                        if largest
                        else None
                    ),
                },
            )
        if intent == AssistantIntent.PROFIT_DECLINE:
            previous = AnalyticsService(self.db).get(
                business_id=business.id,
                date_from=report.previous_period.date_from,
                date_to=report.previous_period.date_to,
                user=user,
            )
            return ToolOutput(
                name=intent.value,
                result={
                    **base,
                    "current": report.summary.model_dump(mode="json"),
                    "previous_period": report.previous_period.model_dump(mode="json"),
                    "previous": previous.summary.model_dump(mode="json"),
                },
            )
        if intent == AssistantIntent.CHANNELS:
            return ToolOutput(
                name=intent.value,
                result={
                    **base,
                    "channels": [channel.model_dump(mode="json") for channel in report.channels],
                },
            )
        return ToolOutput(
            name=AssistantIntent.SUMMARY.value,
            result={
                **base,
                "summary": report.summary.model_dump(mode="json"),
                "previous_period": report.previous_period.model_dump(mode="json"),
                "net_profit_comparison": report.net_profit_comparison.model_dump(mode="json"),
            },
        )
