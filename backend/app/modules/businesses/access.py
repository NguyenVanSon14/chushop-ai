from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.businesses.model import BusinessMember, BusinessRole
from app.modules.businesses.repository import BusinessRepository
from app.modules.users.model import User


def require_business_member(db: Session, *, business_id: UUID, user: User) -> BusinessMember:
    membership = BusinessRepository(db).get_membership(business_id=business_id, user_id=user.id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy doanh nghiệp",
        )
    return membership


def require_business_manager(db: Session, *, business_id: UUID, user: User) -> BusinessMember:
    membership = require_business_member(db, business_id=business_id, user=user)
    if membership.role not in {BusinessRole.OWNER, BusinessRole.MANAGER}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này",
        )
    return membership
