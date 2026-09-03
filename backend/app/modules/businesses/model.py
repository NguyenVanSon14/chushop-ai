from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class BusinessRole(StrEnum):
    OWNER = "OWNER"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="VND")
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Ho_Chi_Minh")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    memberships: Mapped[list["BusinessMember"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )


class BusinessMember(Base):
    __tablename__ = "business_members"
    __table_args__ = (UniqueConstraint("user_id", "business_id", name="uq_business_member"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[BusinessRole] = mapped_column(
        SqlEnum(BusinessRole, name="business_role"), default=BusinessRole.MEMBER
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="memberships")  # noqa: F821
    business: Mapped[Business] = relationship(back_populates="memberships")
