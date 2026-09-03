from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status

from app.core.dependencies import CurrentUser, DbSession
from app.modules.sales.schema import (
    ImportPreview,
    ManualSalesOrderCreate,
    SalesImportRead,
    SalesOrderRead,
)
from app.modules.sales.service import SalesService

router = APIRouter(prefix="/businesses/{business_id}/sales", tags=["sales"])


@router.post("/orders", response_model=SalesOrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    business_id: UUID,
    payload: ManualSalesOrderCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> SalesOrderRead:
    return SalesService(db).create_order(
        business_id=business_id,
        payload=payload,
        user=current_user,
    )


@router.post("/imports/preview", response_model=ImportPreview)
async def preview_import(
    business_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    file: Annotated[UploadFile, File()],
) -> ImportPreview:
    return SalesService(db).preview(
        business_id=business_id,
        filename=file.filename or "import.csv",
        content=await file.read(),
        user=current_user,
    )


@router.post("/imports", response_model=SalesImportRead, status_code=status.HTTP_201_CREATED)
async def create_import(
    business_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    file: Annotated[UploadFile, File()],
) -> SalesImportRead:
    record = SalesService(db).import_file(
        business_id=business_id,
        filename=file.filename or "import.csv",
        content=await file.read(),
        user=current_user,
    )
    return SalesImportRead.model_validate(record)


@router.get("/orders", response_model=list[SalesOrderRead])
def list_orders(
    business_id: UUID, db: DbSession, current_user: CurrentUser
) -> list[SalesOrderRead]:
    return SalesService(db).list_orders(business_id=business_id, user=current_user)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    business_id: UUID,
    order_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    SalesService(db).delete_order(
        business_id=business_id, order_id=order_id, user=current_user
    )


@router.delete("/imports/{import_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_import(
    business_id: UUID,
    import_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    SalesService(db).delete_import(
        business_id=business_id, import_id=import_id, user=current_user
    )
