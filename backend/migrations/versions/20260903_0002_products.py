"""create products table"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_0002"
down_revision: str | None = "20260901_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=True),
        sa.Column("selling_price", sa.BigInteger(), nullable=False),
        sa.Column("cost_price", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("cost_price >= 0", name="ck_product_cost_price_nonnegative"),
        sa.CheckConstraint("selling_price >= 0", name="ck_product_selling_price_nonnegative"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "sku", name="uq_product_business_sku"),
    )
    op.create_index("ix_products_business_id", "products", ["business_id"])


def downgrade() -> None:
    op.drop_index("ix_products_business_id", table_name="products")
    op.drop_table("products")
