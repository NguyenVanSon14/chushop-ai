from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.modules.admin.dependencies import PlatformAdmin
from app.modules.admin.schema import (
    AdminAuditLogRead,
    AdminBusinessRead,
    AdminUserRead,
    AdminUserStatusUpdate,
)
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserRead])
def list_users(db: DbSession, admin: PlatformAdmin) -> list[AdminUserRead]:
    return [AdminUserRead.model_validate(user) for user in AdminService(db).list_users()]


@router.patch("/users/{user_id}/status", response_model=AdminUserRead)
def set_user_status(
    user_id: UUID,
    payload: AdminUserStatusUpdate,
    db: DbSession,
    admin: PlatformAdmin,
) -> AdminUserRead:
    return AdminUserRead.model_validate(
        AdminService(db).set_user_active(
            actor=admin,
            user_id=user_id,
            is_active=payload.is_active,
        )
    )


@router.get("/businesses", response_model=list[AdminBusinessRead])
def list_businesses(db: DbSession, admin: PlatformAdmin) -> list[AdminBusinessRead]:
    return [
        AdminBusinessRead.model_validate(business)
        for business in AdminService(db).list_businesses()
    ]


@router.get("/audit-logs", response_model=list[AdminAuditLogRead])
def list_audit_logs(db: DbSession, admin: PlatformAdmin) -> list[AdminAuditLogRead]:
    return [AdminAuditLogRead.model_validate(log) for log in AdminService(db).list_audit_logs()]
