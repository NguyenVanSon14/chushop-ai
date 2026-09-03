from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.businesses.access import require_business_manager, require_business_member
from app.modules.products.model import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schema import ProductCreate, ProductUpdate
from app.modules.users.model import User


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.products = ProductRepository(db)

    def create(self, *, business_id: UUID, payload: ProductCreate, user: User) -> Product:
        require_business_manager(self.db, business_id=business_id, user=user)
        try:
            product = self.products.add(business_id=business_id, payload=payload)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU đã tồn tại trong doanh nghiệp",
            ) from None
        return product

    def list(self, *, business_id: UUID, user: User) -> list[Product]:
        require_business_member(self.db, business_id=business_id, user=user)
        return self.products.list_for_business(business_id)

    def get(self, *, business_id: UUID, product_id: UUID, user: User) -> Product:
        require_business_member(self.db, business_id=business_id, user=user)
        return self._get_product(business_id=business_id, product_id=product_id)

    def update(
        self, *, business_id: UUID, product_id: UUID, payload: ProductUpdate, user: User
    ) -> Product:
        require_business_manager(self.db, business_id=business_id, user=user)
        product = self._get_product(business_id=business_id, product_id=product_id)
        try:
            product = self.products.update(product, payload)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU đã tồn tại trong doanh nghiệp",
            ) from None
        return product

    def delete(self, *, business_id: UUID, product_id: UUID, user: User) -> None:
        require_business_manager(self.db, business_id=business_id, user=user)
        product = self._get_product(business_id=business_id, product_id=product_id)
        self.products.delete(product)
        self.db.commit()

    def _get_product(self, *, business_id: UUID, product_id: UUID) -> Product:
        product = self.products.get_for_business(business_id=business_id, product_id=product_id)
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy sản phẩm",
            )
        return product
