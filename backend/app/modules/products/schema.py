from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MoneyAmount = Annotated[int, Field(strict=True, ge=0)]


class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    selling_price: MoneyAmount
    cost_price: MoneyAmount
    is_active: bool = True

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str | None) -> str | None:
        return value.upper() if value else None


class ProductUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    selling_price: MoneyAmount | None = None
    cost_price: MoneyAmount | None = None
    is_active: bool | None = None

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str | None) -> str | None:
        return value.upper() if value else None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ProductUpdate":
        if not self.model_fields_set:
            raise ValueError("Cần ít nhất một trường để cập nhật")
        return self


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    name: str
    sku: str | None
    selling_price: int
    cost_price: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
