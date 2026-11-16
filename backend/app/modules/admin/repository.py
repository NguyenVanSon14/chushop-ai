from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.admin.model import AdminAuditLog
from app.modules.businesses.model import Business
from app.modules.users.model import User


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.created_at.desc())).all())

    def get_user(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def list_businesses(self) -> list[Business]:
        return list(self.db.scalars(select(Business).order_by(Business.created_at.desc())).all())

    def add_audit_log(
        self,
        *,
        actor_user_id: UUID,
        action: str,
        target_type: str,
        target_id: str,
        details: dict[str, object],
    ) -> AdminAuditLog:
        log = AdminAuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def list_audit_logs(self, limit: int = 100) -> list[AdminAuditLog]:
        return list(
            self.db.scalars(
                select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit)
            ).all()
        )
