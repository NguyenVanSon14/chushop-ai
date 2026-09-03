"""create assistant conversations and messages"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_0004"
down_revision: str | None = "20260903_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assistant_conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_assistant_conversations_business_id",
        "assistant_conversations",
        ["business_id"],
    )
    op.create_index(
        "ix_assistant_conversations_created_by_id",
        "assistant_conversations",
        ["created_by_id"],
    )
    op.create_table(
        "assistant_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.String(50), nullable=True),
        sa.Column("tool_result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["assistant_conversations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_assistant_messages_conversation_id",
        "assistant_messages",
        ["conversation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_assistant_messages_conversation_id", table_name="assistant_messages")
    op.drop_table("assistant_messages")
    op.drop_index("ix_assistant_conversations_created_by_id", table_name="assistant_conversations")
    op.drop_index("ix_assistant_conversations_business_id", table_name="assistant_conversations")
    op.drop_table("assistant_conversations")
