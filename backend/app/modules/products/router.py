from uuid import UUID

from fastapi import APIRouter, Response, status

from app.core.dependencies import CurrentUser, DbSession
from app.modules.products.schema import ProductCreate, ProductRead, ProductUpdate
from app.modules.products.service import ProductService

router = APIRouter(prefix="/businesses/{business_id}/products", tags=["products"])


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    business_id: UUID,
    payload: ProductCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProductRead:
    return ProductRead.model_validate(
        ProductService(db).create(business_id=business_id, payload=payload, user=current_user)
    )


@router.get("", response_model=list[ProductRead])
def list_products(business_id: UUID, db: DbSession, current_user: CurrentUser) -> list[ProductRead]:
    return [
        ProductRead.model_validate(product)
        for product in ProductService(db).list(business_id=business_id, user=current_user)
    ]


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    business_id: UUID,
    product_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ProductRead:
    return ProductRead.model_validate(
        ProductService(db).get(business_id=business_id, product_id=product_id, user=current_user)
    )


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    business_id: UUID,
    product_id: UUID,
    payload: ProductUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProductRead:
    return ProductRead.model_validate(
        ProductService(db).update(
            business_id=business_id,
            product_id=product_id,
            payload=payload,
            user=current_user,
        )
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    business_id: UUID,
    product_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Response:
    ProductService(db).delete(business_id=business_id, product_id=product_id, user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
