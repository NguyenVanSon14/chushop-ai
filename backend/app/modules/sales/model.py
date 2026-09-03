from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class SalesImport(Base):
    __tablename__ = "sales_imports"
    __table_args__ = (
        UniqueConstraint("business_id", "content_hash", name="uq_sales_import_content_hash"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64))
    row_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    __table_args__ = (
        UniqueConstraint("business_id", "channel", "external_id", name="uq_sales_order_external"),
        CheckConstraint("fees >= 0", name="ck_sales_order_fees_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    sales_import_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("sales_imports.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    external_id: Mapped[str] = mapped_column(String(100))
    channel: Mapped[str] = mapped_column(String(50))
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    fees: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sales_order_item_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_sales_order_item_unit_price_nonnegative"),
        CheckConstraint(
            "cost_price_snapshot >= 0",
            name="ck_sales_order_item_cost_snapshot_nonnegative",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sales_order_id: Mapped[UUID] = mapped_column(
        ForeignKey("sales_orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    product_name_snapshot: Mapped[str] = mapped_column(String(255))
    sku_snapshot: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[int] = mapped_column(BigInteger)
    cost_price_snapshot: Mapped[int] = mapped_column(BigInteger)
