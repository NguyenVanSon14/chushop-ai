from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.admin.model import AdminAuditLog
from app.modules.admin.repository import AdminRepository
from app.modules.businesses.model import Business
from app.modules.users.model import User


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminRepository(db)

    def list_users(self) -> list[User]:
        return self.repository.list_users()

    def list_businesses(self) -> list[Business]:
        return self.repository.list_businesses()

    def list_audit_logs(self) -> list[AdminAuditLog]:
        return self.repository.list_audit_logs()

    def set_user_active(self, *, actor: User, user_id: UUID, is_active: bool) -> User:
        target = self.repository.get_user(user_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        if target.id == actor.id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Admin không thể tự khóa tài khoản đang sử dụng",
            )
        previous = target.is_active
        target.is_active = is_active
        self.repository.add_audit_log(
            actor_user_id=actor.id,
            action="USER_STATUS_CHANGED",
            target_type="USER",
            target_id=str(target.id),
            details={"previous_is_active": previous, "is_active": is_active},
        )
        self.db.commit()
        return target
