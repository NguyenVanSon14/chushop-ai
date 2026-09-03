from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveMoney = Annotated[int, Field(strict=True, gt=0)]


class ExpenseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    amount: PositiveMoney
    incurred_on: date


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    amount: PositiveMoney | None = None
    incurred_on: date | None = None

    @model_validator(mode="after")
    def require_fields(self) -> "ExpenseUpdate":
        if not self.model_fields_set:
            raise ValueError("Cần ít nhất một trường để cập nhật")
        return self


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    description: str
    category: str
    amount: int
    incurred_on: date
    created_at: datetime
    updated_at: datetime
