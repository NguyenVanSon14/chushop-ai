from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    is_active: bool
    is_platform_admin: bool
    created_at: datetime


class AdminBusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    currency: str
    timezone: str
    created_at: datetime


class AdminUserStatusUpdate(BaseModel):
    is_active: bool


class AdminAuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_user_id: UUID
    action: str
    target_type: str
    target_id: str
    details: dict[str, Any]
    created_at: datetime
