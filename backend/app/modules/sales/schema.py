from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MoneyAmount = Annotated[int, Field(strict=True, ge=0)]


class ImportPreviewRow(BaseModel):
    order_code: str
    channel: str
    ordered_at: datetime
    sku: str
    product_name: str
    quantity: int
    unit_price: int
    cost_price_snapshot: int
    fees: int

    @property
    def revenue(self) -> int:
        return self.quantity * self.unit_price

    @property
    def cost(self) -> int:
        return self.quantity * self.cost_price_snapshot


class ImportPreview(BaseModel):
    filename: str
    row_count: int
    order_count: int
    total_revenue: int
    total_cost: int
    total_fees: int
    rows: list[ImportPreviewRow]


class SalesImportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    filename: str
    row_count: int
    created_at: datetime


class SalesOrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID | None
    product_name_snapshot: str
    sku_snapshot: str
    quantity: int
    unit_price: int
    cost_price_snapshot: int
    revenue: int
    cogs: int


class SalesOrderRead(BaseModel):
    id: UUID
    business_id: UUID
    external_id: str
    channel: str
    ordered_at: datetime
    fees: int
    revenue: int
    cogs: int
    items: list[SalesOrderItemRead]


class ManualSalesOrderItemCreate(BaseModel):
    product_id: UUID
    quantity: Annotated[int, Field(strict=True, gt=0, le=10_000)]
    unit_price: MoneyAmount


class ManualSalesOrderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    order_code: str | None = Field(default=None, max_length=100)
    channel: str = Field(min_length=1, max_length=50)
    ordered_at: datetime
    fees: MoneyAmount = 0
    items: list[ManualSalesOrderItemCreate] = Field(min_length=1, max_length=50)

    @field_validator("channel")
    @classmethod
    def normalize_channel(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def reject_duplicate_products(self) -> "ManualSalesOrderCreate":
        product_ids = [item.product_id for item in self.items]
        if len(set(product_ids)) != len(product_ids):
            raise ValueError("Mỗi sản phẩm chỉ được xuất hiện một lần trong đơn")
        return self


class RawImportRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    order_code: str = Field(min_length=1, max_length=100)
    channel: str = Field(min_length=1, max_length=50)
    ordered_at: datetime
    sku: str = Field(min_length=1, max_length=100)
    quantity: int = Field(strict=True, gt=0)
    unit_price: int = Field(strict=True, ge=0)
    fees: int = Field(strict=True, ge=0)
