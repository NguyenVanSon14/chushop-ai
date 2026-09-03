from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConversationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(default="Cuộc trò chuyện mới", min_length=1, max_length=120)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class AssistantMessageCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=2, max_length=1000)
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "AssistantMessageCreate":
        if (self.date_from is None) != (self.date_to is None):
            raise ValueError("Cần cung cấp cả ngày bắt đầu và ngày kết thúc")
        return self


class AssistantMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    tool_name: str | None
    tool_result: dict[str, Any] | None
    created_at: datetime


class ConversationDetail(ConversationRead):
    messages: list[AssistantMessageRead]


class AssistantReply(BaseModel):
    user_message: AssistantMessageRead
    assistant_message: AssistantMessageRead
