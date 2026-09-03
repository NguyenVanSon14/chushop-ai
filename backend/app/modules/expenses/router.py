from uuid import UUID

from fastapi import APIRouter, Response, status

from app.core.dependencies import CurrentUser, DbSession
from app.modules.expenses.schema import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.modules.expenses.service import ExpenseService

router = APIRouter(prefix="/businesses/{business_id}/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    business_id: UUID,
    payload: ExpenseCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ExpenseRead:
    return ExpenseRead.model_validate(
        ExpenseService(db).create(business_id=business_id, payload=payload, user=current_user)
    )


@router.get("", response_model=list[ExpenseRead])
def list_expenses(business_id: UUID, db: DbSession, current_user: CurrentUser) -> list[ExpenseRead]:
    return [
        ExpenseRead.model_validate(expense)
        for expense in ExpenseService(db).list(business_id=business_id, user=current_user)
    ]


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    business_id: UUID,
    expense_id: UUID,
    payload: ExpenseUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ExpenseRead:
    return ExpenseRead.model_validate(
        ExpenseService(db).update(
            business_id=business_id,
            expense_id=expense_id,
            payload=payload,
            user=current_user,
        )
    )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    business_id: UUID,
    expense_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    ExpenseService(db).delete(business_id=business_id, expense_id=expense_id, user=current_user)
    return Response(status_code=204)
