from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schema import (
    AnalyticsPeriod,
    AnalyticsRead,
    AnalyticsSummary,
    ChannelProfitability,
    MetricComparison,
    ProductProfitability,
    TrendPoint,
)
from app.modules.businesses.access import require_business_member
from app.modules.businesses.model import Business
from app.modules.expenses.model import Expense
from app.modules.sales.model import SalesOrder, SalesOrderItem
from app.modules.users.model import User


def ratio_bps(numerator: int, denominator: int) -> int | None:
    if denominator == 0:
        return None
    value = Decimal(numerator) * Decimal(10_000) / Decimal(abs(denominator))
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class Totals:
    order_count: int = 0
    revenue: int = 0
    cogs: int = 0
    fees: int = 0
    expenses: int = 0

    @property
    def gross_profit(self) -> int:
        return self.revenue - self.cogs

    @property
    def net_profit(self) -> int:
        return self.gross_profit - self.fees - self.expenses


@dataclass
class ProductTotals:
    sku: str
    name: str
    quantity: int = 0
    revenue: int = 0
    cogs: int = 0


@dataclass
class ChannelTotals:
    channel: str
    order_ids: set[UUID] = field(default_factory=set)
    revenue: int = 0
    cogs: int = 0
    fees: int = 0


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.analytics = AnalyticsRepository(db)

    def get(
        self, *, business_id: UUID, date_from: date, date_to: date, user: User
    ) -> AnalyticsRead:
        require_business_member(self.db, business_id=business_id, user=user)
        self._validate_period(date_from, date_to)
        business = self.db.get(Business, business_id)
        if business is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy doanh nghiệp")
        timezone = ZoneInfo(business.timezone)
        days = (date_to - date_from).days + 1
        previous_to = date_from - timedelta(days=1)
        previous_from = previous_to - timedelta(days=days - 1)

        orders, items, expenses = self._load_period(
            business_id=business_id,
            date_from=date_from,
            date_to=date_to,
            timezone=timezone,
        )
        previous_orders, previous_items, previous_expenses = self._load_period(
            business_id=business_id,
            date_from=previous_from,
            date_to=previous_to,
            timezone=timezone,
        )
        totals = self._totals(orders, items, expenses)
        previous = self._totals(previous_orders, previous_items, previous_expenses)
        return AnalyticsRead(
            period=AnalyticsPeriod(date_from=date_from, date_to=date_to),
            previous_period=AnalyticsPeriod(date_from=previous_from, date_to=previous_to),
            summary=self._summary(totals),
            revenue_comparison=self._comparison(totals.revenue, previous.revenue),
            net_profit_comparison=self._comparison(totals.net_profit, previous.net_profit),
            trends=self._trends(
                date_from=date_from,
                date_to=date_to,
                timezone=timezone,
                orders=orders,
                items=items,
                expenses=expenses,
            ),
            products=self._products(items),
            channels=self._channels(orders, items),
        )

    def _load_period(
        self,
        *,
        business_id: UUID,
        date_from: date,
        date_to: date,
        timezone: ZoneInfo,
    ) -> tuple[list[SalesOrder], list[SalesOrderItem], list[Expense]]:
        start = datetime.combine(date_from, time.min, timezone).astimezone(UTC)
        end = datetime.combine(date_to + timedelta(days=1), time.min, timezone).astimezone(UTC)
        orders = self.analytics.orders(business_id=business_id, start=start, end=end)
        items = self.analytics.items([order.id for order in orders])
        expenses = self.analytics.expenses(business_id=business_id, start=date_from, end=date_to)
        return orders, items, expenses

    @staticmethod
    def _validate_period(date_from: date, date_to: date) -> None:
        if date_from > date_to:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Ngày bắt đầu phải trước ngày kết thúc",
            )
        if (date_to - date_from).days >= 366:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Khoảng thời gian tối đa là 366 ngày",
            )

    @staticmethod
    def _totals(
        orders: list[SalesOrder], items: list[SalesOrderItem], expenses: list[Expense]
    ) -> Totals:
        return Totals(
            order_count=len(orders),
            revenue=sum(item.quantity * item.unit_price for item in items),
            cogs=sum(item.quantity * item.cost_price_snapshot for item in items),
            fees=sum(order.fees for order in orders),
            expenses=sum(expense.amount for expense in expenses),
        )

    @staticmethod
    def _summary(totals: Totals) -> AnalyticsSummary:
        return AnalyticsSummary(
            order_count=totals.order_count,
            revenue=totals.revenue,
            cogs=totals.cogs,
            fees=totals.fees,
            gross_profit=totals.gross_profit,
            expenses=totals.expenses,
            net_profit=totals.net_profit,
            gross_margin_bps=ratio_bps(totals.gross_profit, totals.revenue),
            net_margin_bps=ratio_bps(totals.net_profit, totals.revenue),
        )

    @staticmethod
    def _comparison(current: int, previous: int) -> MetricComparison:
        difference = current - previous
        return MetricComparison(
            current=current,
            previous=previous,
            difference=difference,
            change_bps=ratio_bps(difference, previous),
        )

    @staticmethod
    def _products(items: list[SalesOrderItem]) -> list[ProductProfitability]:
        grouped: dict[tuple[str, str], ProductTotals] = {}
        for item in items:
            key = (item.sku_snapshot, item.product_name_snapshot)
            totals = grouped.setdefault(
                key, ProductTotals(sku=item.sku_snapshot, name=item.product_name_snapshot)
            )
            totals.quantity += item.quantity
            totals.revenue += item.quantity * item.unit_price
            totals.cogs += item.quantity * item.cost_price_snapshot
        result = [
            ProductProfitability(
                sku=value.sku,
                name=value.name,
                quantity=value.quantity,
                revenue=value.revenue,
                cogs=value.cogs,
                gross_profit=value.revenue - value.cogs,
                gross_margin_bps=ratio_bps(value.revenue - value.cogs, value.revenue),
            )
            for value in grouped.values()
        ]
        return sorted(result, key=lambda item: item.gross_profit, reverse=True)

    @staticmethod
    def _channels(
        orders: list[SalesOrder], items: list[SalesOrderItem]
    ) -> list[ChannelProfitability]:
        order_map = {order.id: order for order in orders}
        grouped: dict[str, ChannelTotals] = {}
        for order in orders:
            totals = grouped.setdefault(order.channel, ChannelTotals(channel=order.channel))
            totals.order_ids.add(order.id)
            totals.fees += order.fees
        for item in items:
            order = order_map[item.sales_order_id]
            totals = grouped[order.channel]
            totals.revenue += item.quantity * item.unit_price
            totals.cogs += item.quantity * item.cost_price_snapshot
        result = []
        for value in grouped.values():
            contribution = value.revenue - value.cogs - value.fees
            result.append(
                ChannelProfitability(
                    channel=value.channel,
                    order_count=len(value.order_ids),
                    revenue=value.revenue,
                    cogs=value.cogs,
                    fees=value.fees,
                    contribution_profit=contribution,
                    contribution_margin_bps=ratio_bps(contribution, value.revenue),
                )
            )
        return sorted(result, key=lambda item: item.contribution_profit, reverse=True)

    @staticmethod
    def _trends(
        *,
        date_from: date,
        date_to: date,
        timezone: ZoneInfo,
        orders: list[SalesOrder],
        items: list[SalesOrderItem],
        expenses: list[Expense],
    ) -> list[TrendPoint]:
        order_map = {order.id: order for order in orders}
        daily: dict[date, Totals] = defaultdict(Totals)
        for order in orders:
            ordered_at = order.ordered_at
            if ordered_at.tzinfo is None:
                ordered_at = ordered_at.replace(tzinfo=UTC)
            day = ordered_at.astimezone(timezone).date()
            daily[day].order_count += 1
            daily[day].fees += order.fees
        for item in items:
            ordered_at = order_map[item.sales_order_id].ordered_at
            if ordered_at.tzinfo is None:
                ordered_at = ordered_at.replace(tzinfo=UTC)
            totals = daily[ordered_at.astimezone(timezone).date()]
            totals.revenue += item.quantity * item.unit_price
            totals.cogs += item.quantity * item.cost_price_snapshot
        for expense in expenses:
            daily[expense.incurred_on].expenses += expense.amount
        return [
            TrendPoint(
                date=date_from + timedelta(days=index),
                revenue=daily[date_from + timedelta(days=index)].revenue,
                cogs=daily[date_from + timedelta(days=index)].cogs,
                fees=daily[date_from + timedelta(days=index)].fees,
                expenses=daily[date_from + timedelta(days=index)].expenses,
                net_profit=daily[date_from + timedelta(days=index)].net_profit,
            )
            for index in range((date_to - date_from).days + 1)
        ]
