"""allow sales orders created without an import"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_0005"
down_revision: str | None = "20260903_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("sales_orders") as batch_op:
        batch_op.alter_column(
            "sales_import_id",
            existing_type=sa.Uuid(),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("sales_orders") as batch_op:
        batch_op.alter_column(
            "sales_import_id",
            existing_type=sa.Uuid(),
            nullable=False,
        )
