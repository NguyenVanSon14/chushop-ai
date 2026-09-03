from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_expense_amount_positive"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    amount: Mapped[int] = mapped_column(BigInteger)
    incurred_on: Mapped[date] = mapped_column(Date, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
