from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products.model import Product
from app.modules.sales.model import SalesImport, SalesOrder, SalesOrderItem


class SalesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def import_exists(self, *, business_id: UUID, content_hash: str) -> bool:
        return (
            self.db.scalar(
                select(SalesImport.id).where(
                    SalesImport.business_id == business_id,
                    SalesImport.content_hash == content_hash,
                )
            )
            is not None
        )

    def products_by_sku(self, *, business_id: UUID, skus: set[str]) -> dict[str, Product]:
        products = self.db.scalars(
            select(Product).where(Product.business_id == business_id, Product.sku.in_(skus))
        )
        return {product.sku: product for product in products if product.sku is not None}

    def products_by_id(self, *, business_id: UUID, product_ids: set[UUID]) -> dict[UUID, Product]:
        products = self.db.scalars(
            select(Product).where(
                Product.business_id == business_id,
                Product.id.in_(product_ids),
            )
        )
        return {product.id: product for product in products}

    def add_import(
        self, *, business_id: UUID, filename: str, content_hash: str, row_count: int
    ) -> SalesImport:
        record = SalesImport(
            business_id=business_id,
            filename=filename,
            content_hash=content_hash,
            row_count=row_count,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def add_order(
        self,
        *,
        business_id: UUID,
        sales_import_id: UUID | None,
        external_id: str,
        channel: str,
        ordered_at: datetime,
        fees: int,
    ) -> SalesOrder:
        order = SalesOrder(
            business_id=business_id,
            sales_import_id=sales_import_id,
            external_id=external_id,
            channel=channel,
            ordered_at=ordered_at,
            fees=fees,
        )
        self.db.add(order)
        self.db.flush()
        return order

    def add_item(
        self,
        *,
        sales_order_id: UUID,
        product: Product,
        quantity: int,
        unit_price: int,
    ) -> SalesOrderItem:
        item = SalesOrderItem(
            sales_order_id=sales_order_id,
            product_id=product.id,
            product_name_snapshot=product.name,
            sku_snapshot=product.sku or "",
            quantity=quantity,
            unit_price=unit_price,
            cost_price_snapshot=product.cost_price,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def list_orders(self, business_id: UUID) -> list[SalesOrder]:
        return list(
            self.db.scalars(
                select(SalesOrder)
                .where(SalesOrder.business_id == business_id)
                .order_by(SalesOrder.ordered_at.desc(), SalesOrder.created_at.desc())
            ).all()
        )

    def items_for_orders(self, order_ids: list[UUID]) -> list[SalesOrderItem]:
        if not order_ids:
            return []
        return list(
            self.db.scalars(
                select(SalesOrderItem).where(SalesOrderItem.sales_order_id.in_(order_ids))
            ).all()
        )

    def get_order(self, *, order_id: UUID, business_id: UUID) -> SalesOrder | None:
        return self.db.scalar(
            select(SalesOrder).where(
                SalesOrder.id == order_id,
                SalesOrder.business_id == business_id,
            )
        )

    def delete_order(self, order: SalesOrder) -> None:
        self.db.delete(order)
        self.db.flush()

    def get_import(self, *, import_id: UUID, business_id: UUID) -> SalesImport | None:
        return self.db.scalar(
            select(SalesImport).where(
                SalesImport.id == import_id,
                SalesImport.business_id == business_id,
            )
        )

    def orders_by_import(self, import_id: UUID) -> list[SalesOrder]:
        return list(
            self.db.scalars(select(SalesOrder).where(SalesOrder.sales_import_id == import_id)).all()
        )

    def delete_import(self, record: SalesImport) -> None:
        self.db.delete(record)
        self.db.flush()
