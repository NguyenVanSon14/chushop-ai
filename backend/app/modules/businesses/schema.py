from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.businesses.model import BusinessRole


class BusinessCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class BusinessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    currency: str
    timezone: str
    created_at: datetime
    updated_at: datetime


class BusinessMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    business_id: UUID
    role: BusinessRole
    created_at: datetime
