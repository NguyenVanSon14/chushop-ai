from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.modules.businesses.schema import BusinessCreate, BusinessRead
from app.modules.businesses.service import BusinessService

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
def create_business(
    payload: BusinessCreate, db: DbSession, current_user: CurrentUser
) -> BusinessRead:
    return BusinessRead.model_validate(
        BusinessService(db).create(payload=payload, creator=current_user)
    )


@router.get("", response_model=list[BusinessRead])
def list_businesses(db: DbSession, current_user: CurrentUser) -> list[BusinessRead]:
    return [
        BusinessRead.model_validate(item)
        for item in BusinessService(db).list_for_user(current_user)
    ]


@router.get("/{business_id}", response_model=BusinessRead)
def get_business(business_id: UUID, db: DbSession, current_user: CurrentUser) -> BusinessRead:
    return BusinessRead.model_validate(
        BusinessService(db).get_for_user(business_id=business_id, user=current_user)
    )
