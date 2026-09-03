from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.assistant.model import AssistantConversation, AssistantMessage


class AssistantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_conversation(
        self, *, business_id: UUID, created_by_id: UUID, title: str
    ) -> AssistantConversation:
        conversation = AssistantConversation(
            business_id=business_id,
            created_by_id=created_by_id,
            title=title,
        )
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def list_conversations(self, business_id: UUID) -> list[AssistantConversation]:
        return list(
            self.db.scalars(
                select(AssistantConversation)
                .where(AssistantConversation.business_id == business_id)
                .order_by(AssistantConversation.updated_at.desc())
            ).all()
        )

    def get_conversation(
        self, *, business_id: UUID, conversation_id: UUID
    ) -> AssistantConversation | None:
        return self.db.scalar(
            select(AssistantConversation).where(
                AssistantConversation.id == conversation_id,
                AssistantConversation.business_id == business_id,
            )
        )

    def list_messages(self, conversation_id: UUID) -> list[AssistantMessage]:
        return list(
            self.db.scalars(
                select(AssistantMessage)
                .where(AssistantMessage.conversation_id == conversation_id)
                .order_by(AssistantMessage.created_at, AssistantMessage.id)
            ).all()
        )

    def add_message(
        self,
        *,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_name: str | None = None,
        tool_result: dict[str, object] | None = None,
    ) -> AssistantMessage:
        message = AssistantMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_result=tool_result,
        )
        self.db.add(message)
        self.db.flush()
        return message
