from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.expenses.model import Expense
from app.modules.sales.model import SalesOrder, SalesOrderItem


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def orders(self, *, business_id: UUID, start: datetime, end: datetime) -> list[SalesOrder]:
        return list(
            self.db.scalars(
                select(SalesOrder).where(
                    SalesOrder.business_id == business_id,
                    SalesOrder.ordered_at >= start,
                    SalesOrder.ordered_at < end,
                )
            ).all()
        )

    def items(self, order_ids: list[UUID]) -> list[SalesOrderItem]:
        if not order_ids:
            return []
        return list(
            self.db.scalars(
                select(SalesOrderItem).where(SalesOrderItem.sales_order_id.in_(order_ids))
            ).all()
        )

    def expenses(self, *, business_id: UUID, start: date, end: date) -> list[Expense]:
        return list(
            self.db.scalars(
                select(Expense).where(
                    Expense.business_id == business_id,
                    Expense.incurred_on >= start,
                    Expense.incurred_on <= end,
                )
            ).all()
        )
