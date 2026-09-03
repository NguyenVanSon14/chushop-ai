"""create sales imports, orders, items, and expenses"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_0003"
down_revision: str | None = "20260903_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sales_imports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "content_hash", name="uq_sales_import_content_hash"),
    )
    op.create_index("ix_sales_imports_business_id", "sales_imports", ["business_id"])
    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("sales_import_id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.String(100), nullable=False),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("ordered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fees", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("fees >= 0", name="ck_sales_order_fees_nonnegative"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sales_import_id"], ["sales_imports.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "business_id", "channel", "external_id", name="uq_sales_order_external"
        ),
    )
    op.create_index("ix_sales_orders_business_id", "sales_orders", ["business_id"])
    op.create_index("ix_sales_orders_sales_import_id", "sales_orders", ["sales_import_id"])
    op.create_index("ix_sales_orders_ordered_at", "sales_orders", ["ordered_at"])
    op.create_table(
        "sales_order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sales_order_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=True),
        sa.Column("product_name_snapshot", sa.String(255), nullable=False),
        sa.Column("sku_snapshot", sa.String(100), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.BigInteger(), nullable=False),
        sa.Column("cost_price_snapshot", sa.BigInteger(), nullable=False),
        sa.CheckConstraint(
            "cost_price_snapshot >= 0",
            name="ck_sales_order_item_cost_snapshot_nonnegative",
        ),
        sa.CheckConstraint("quantity > 0", name="ck_sales_order_item_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_sales_order_item_unit_price_nonnegative"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sales_order_items_sales_order_id", "sales_order_items", ["sales_order_id"])
    op.create_index("ix_sales_order_items_product_id", "sales_order_items", ["product_id"])
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("incurred_on", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_expense_amount_positive"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expenses_business_id", "expenses", ["business_id"])
    op.create_index("ix_expenses_incurred_on", "expenses", ["incurred_on"])


def downgrade() -> None:
    op.drop_index("ix_expenses_incurred_on", table_name="expenses")
    op.drop_index("ix_expenses_business_id", table_name="expenses")
    op.drop_table("expenses")
    op.drop_index("ix_sales_order_items_product_id", table_name="sales_order_items")
    op.drop_index("ix_sales_order_items_sales_order_id", table_name="sales_order_items")
    op.drop_table("sales_order_items")
    op.drop_index("ix_sales_orders_ordered_at", table_name="sales_orders")
    op.drop_index("ix_sales_orders_sales_import_id", table_name="sales_orders")
    op.drop_index("ix_sales_orders_business_id", table_name="sales_orders")
    op.drop_table("sales_orders")
    op.drop_index("ix_sales_imports_business_id", table_name="sales_imports")
    op.drop_table("sales_imports")
