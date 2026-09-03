from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.businesses.model import Business, BusinessMember, BusinessRole


class BusinessRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def slug_exists(self, slug: str) -> bool:
        return self.db.scalar(select(Business.id).where(Business.slug == slug)) is not None

    def add(self, *, name: str, slug: str) -> Business:
        business = Business(name=name, slug=slug)
        self.db.add(business)
        self.db.flush()
        return business

    def add_member(self, *, user_id: UUID, business_id: UUID, role: BusinessRole) -> BusinessMember:
        membership = BusinessMember(user_id=user_id, business_id=business_id, role=role)
        self.db.add(membership)
        self.db.flush()
        return membership

    def list_for_user(self, user_id: UUID) -> list[Business]:
        statement = (
            select(Business)
            .join(BusinessMember)
            .where(BusinessMember.user_id == user_id)
            .order_by(Business.created_at)
        )
        return list(self.db.scalars(statement).all())

    def get_for_user(self, *, business_id: UUID, user_id: UUID) -> Business | None:
        statement = (
            select(Business)
            .join(BusinessMember)
            .where(Business.id == business_id, BusinessMember.user_id == user_id)
        )
        return self.db.scalar(statement)

    def get_membership(self, *, business_id: UUID, user_id: UUID) -> BusinessMember | None:
        return self.db.scalar(
            select(BusinessMember).where(
                BusinessMember.business_id == business_id,
                BusinessMember.user_id == user_id,
            )
        )
