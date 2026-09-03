from datetime import date

from pydantic import BaseModel


class AnalyticsPeriod(BaseModel):
    date_from: date
    date_to: date


class MetricComparison(BaseModel):
    current: int
    previous: int
    difference: int
    change_bps: int | None


class AnalyticsSummary(BaseModel):
    order_count: int
    revenue: int
    cogs: int
    fees: int
    gross_profit: int
    expenses: int
    net_profit: int
    gross_margin_bps: int | None
    net_margin_bps: int | None


class TrendPoint(BaseModel):
    date: date
    revenue: int
    cogs: int
    fees: int
    expenses: int
    net_profit: int


class ProductProfitability(BaseModel):
    sku: str
    name: str
    quantity: int
    revenue: int
    cogs: int
    gross_profit: int
    gross_margin_bps: int | None


class ChannelProfitability(BaseModel):
    channel: str
    order_count: int
    revenue: int
    cogs: int
    fees: int
    contribution_profit: int
    contribution_margin_bps: int | None


class AnalyticsRead(BaseModel):
    period: AnalyticsPeriod
    previous_period: AnalyticsPeriod
    summary: AnalyticsSummary
    revenue_comparison: MetricComparison
    net_profit_comparison: MetricComparison
    trends: list[TrendPoint]
    products: list[ProductProfitability]
    channels: list[ChannelProfitability]
