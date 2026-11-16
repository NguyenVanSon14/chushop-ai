from datetime import date
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations.llm.client import get_llm_provider
from app.modules.assistant.model import AssistantConversation, utc_now
from app.modules.assistant.repository import AssistantRepository
from app.modules.assistant.schema import (
    AssistantMessageCreate,
    AssistantReply,
    ConversationCreate,
    ConversationDetail,
)
from app.modules.assistant.tools import (
    AnalyticsToolExecutor,
    AssistantIntent,
    ToolOutput,
    classify_intent,
)
from app.modules.businesses.access import require_business_member
from app.modules.businesses.model import Business
from app.modules.users.model import User


class AssistantService:
    def __init__(
        self,
        db: Session,
        explanation_provider: Any = None,
    ) -> None:
        self.db = db
        self.repository = AssistantRepository(db)
        self.tools = AnalyticsToolExecutor(db)
        self.explanation_provider = explanation_provider or get_llm_provider()

    def create_conversation(
        self, *, business_id: UUID, payload: ConversationCreate, user: User
    ) -> AssistantConversation:
        require_business_member(self.db, business_id=business_id, user=user)
        conversation = self.repository.add_conversation(
            business_id=business_id,
            created_by_id=user.id,
            title=payload.title.strip(),
        )
        self.db.commit()
        return conversation

    def list_conversations(self, *, business_id: UUID, user: User) -> list[AssistantConversation]:
        require_business_member(self.db, business_id=business_id, user=user)
        return self.repository.list_conversations(business_id)

    def get_conversation(
        self, *, business_id: UUID, conversation_id: UUID, user: User
    ) -> ConversationDetail:
        require_business_member(self.db, business_id=business_id, user=user)
        conversation = self._conversation(business_id=business_id, conversation_id=conversation_id)
        return ConversationDetail.model_validate(
            {
                **conversation.__dict__,
                "messages": self.repository.list_messages(conversation.id),
            }
        )

    def ask(
        self,
        *,
        business_id: UUID,
        conversation_id: UUID,
        payload: AssistantMessageCreate,
        user: User,
    ) -> AssistantReply:
        require_business_member(self.db, business_id=business_id, user=user)
        conversation = self._conversation(business_id=business_id, conversation_id=conversation_id)
        business = self.db.get(Business, business_id)
        if business is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy doanh nghiệp")
        date_from, date_to = self._period(business, payload.date_from, payload.date_to)
        question = payload.question.strip()

        def execute_tool(intent: AssistantIntent) -> ToolOutput:
            return self.tools.execute(
                intent=intent,
                business=business,
                user=user,
                date_from=date_from,
                date_to=date_to,
            )

        if hasattr(self.explanation_provider, "process_question"):
            output, answer = self.explanation_provider.process_question(question, execute_tool)
        else:
            intent = classify_intent(question)
            output = execute_tool(intent)
            answer = self.explanation_provider.explain(output)

        user_message = self.repository.add_message(
            conversation_id=conversation.id,
            role="USER",
            content=question,
        )
        assistant_message = self.repository.add_message(
            conversation_id=conversation.id,
            role="ASSISTANT",
            content=answer,
            tool_name=output.name,
            tool_result=output.result,
        )
        if conversation.title == "Cuộc trò chuyện mới":
            conversation.title = question[:120]
        conversation.updated_at = utc_now()
        self.db.commit()
        return AssistantReply(
            user_message=user_message,
            assistant_message=assistant_message,
        )

    def _conversation(self, *, business_id: UUID, conversation_id: UUID) -> AssistantConversation:
        conversation = self.repository.get_conversation(
            business_id=business_id,
            conversation_id=conversation_id,
        )
        if conversation is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện")
        return conversation

    def _period(
        self,
        business: Business,
        date_from: date | None,
        date_to: date | None,
    ) -> tuple[date, date]:
        if date_from is not None and date_to is not None:
            return date_from, date_to
        return self.tools.default_period(business)
