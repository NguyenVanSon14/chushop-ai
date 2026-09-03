from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products.model import Product
from app.modules.products.schema import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, *, business_id: UUID, payload: ProductCreate) -> Product:
        product = Product(
            business_id=business_id,
            name=payload.name,
            sku=payload.sku or None,
            selling_price=payload.selling_price,
            cost_price=payload.cost_price,
            is_active=payload.is_active,
        )
        self.db.add(product)
        self.db.flush()
        return product

    def list_for_business(self, business_id: UUID) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.business_id == business_id)
            .order_by(Product.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_for_business(self, *, business_id: UUID, product_id: UUID) -> Product | None:
        return self.db.scalar(
            select(Product).where(
                Product.id == product_id,
                Product.business_id == business_id,
            )
        )

    def update(self, product: Product, payload: ProductUpdate) -> Product:
        values = payload.model_dump(exclude_unset=True)
        if "sku" in values:
            values["sku"] = values["sku"] or None
        for field, value in values.items():
            setattr(product, field, value)
        self.db.flush()
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()
