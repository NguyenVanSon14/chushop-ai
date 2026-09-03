from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.businesses.access import require_business_manager, require_business_member
from app.modules.expenses.model import Expense
from app.modules.expenses.repository import ExpenseRepository
from app.modules.expenses.schema import ExpenseCreate, ExpenseUpdate
from app.modules.users.model import User


class ExpenseService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.expenses = ExpenseRepository(db)

    def create(self, *, business_id: UUID, payload: ExpenseCreate, user: User) -> Expense:
        require_business_manager(self.db, business_id=business_id, user=user)
        expense = self.expenses.add(business_id=business_id, payload=payload)
        self.db.commit()
        return expense

    def list(self, *, business_id: UUID, user: User) -> list[Expense]:
        require_business_member(self.db, business_id=business_id, user=user)
        return self.expenses.list(business_id)

    def update(
        self, *, business_id: UUID, expense_id: UUID, payload: ExpenseUpdate, user: User
    ) -> Expense:
        require_business_manager(self.db, business_id=business_id, user=user)
        expense = self._get(business_id=business_id, expense_id=expense_id)
        expense = self.expenses.update(expense, payload)
        self.db.commit()
        return expense

    def delete(self, *, business_id: UUID, expense_id: UUID, user: User) -> None:
        require_business_manager(self.db, business_id=business_id, user=user)
        expense = self._get(business_id=business_id, expense_id=expense_id)
        self.expenses.delete(expense)
        self.db.commit()

    def _get(self, *, business_id: UUID, expense_id: UUID) -> Expense:
        expense = self.expenses.get(business_id=business_id, expense_id=expense_id)
        if expense is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy chi phí")
        return expense
