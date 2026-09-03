from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.expenses.model import Expense
from app.modules.expenses.schema import ExpenseCreate, ExpenseUpdate


class ExpenseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, *, business_id: UUID, payload: ExpenseCreate) -> Expense:
        expense = Expense(business_id=business_id, **payload.model_dump())
        self.db.add(expense)
        self.db.flush()
        return expense

    def list(self, business_id: UUID) -> list[Expense]:
        return list(
            self.db.scalars(
                select(Expense)
                .where(Expense.business_id == business_id)
                .order_by(Expense.incurred_on.desc(), Expense.created_at.desc())
            ).all()
        )

    def get(self, *, business_id: UUID, expense_id: UUID) -> Expense | None:
        return self.db.scalar(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.business_id == business_id,
            )
        )

    def update(self, expense: Expense, payload: ExpenseUpdate) -> Expense:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(expense, field, value)
        self.db.flush()
        return expense

    def delete(self, expense: Expense) -> None:
        self.db.delete(expense)
        self.db.flush()
