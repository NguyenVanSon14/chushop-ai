import re
import unicodedata
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.businesses.model import Business, BusinessRole
from app.modules.businesses.repository import BusinessRepository
from app.modules.businesses.schema import BusinessCreate
from app.modules.users.model import User


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "business"


class BusinessService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.businesses = BusinessRepository(db)

    def create(self, *, payload: BusinessCreate, creator: User) -> Business:
        name = payload.name.strip()
        base_slug = slugify(name)
        slug = base_slug
        suffix = 2
        while self.businesses.slug_exists(slug):
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        try:
            business = self.businesses.add(name=name, slug=slug)
            self.businesses.add_member(
                user_id=creator.id, business_id=business.id, role=BusinessRole.OWNER
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return business

    def list_for_user(self, user: User) -> list[Business]:
        return self.businesses.list_for_user(user.id)

    def get_for_user(self, *, business_id: UUID, user: User) -> Business:
        business = self.businesses.get_for_user(business_id=business_id, user_id=user.id)
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy doanh nghiệp"
            )
        return business
