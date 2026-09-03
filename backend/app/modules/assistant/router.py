from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.modules.assistant.schema import (
    AssistantMessageCreate,
    AssistantReply,
    ConversationCreate,
    ConversationDetail,
    ConversationRead,
)
from app.modules.assistant.service import AssistantService

router = APIRouter(prefix="/businesses/{business_id}/assistant", tags=["assistant"])


@router.post(
    "/conversations",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    business_id: UUID,
    payload: ConversationCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ConversationRead:
    return ConversationRead.model_validate(
        AssistantService(db).create_conversation(
            business_id=business_id,
            payload=payload,
            user=current_user,
        )
    )


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(
    business_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> list[ConversationRead]:
    return [
        ConversationRead.model_validate(conversation)
        for conversation in AssistantService(db).list_conversations(
            business_id=business_id, user=current_user
        )
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    business_id: UUID,
    conversation_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ConversationDetail:
    return AssistantService(db).get_conversation(
        business_id=business_id,
        conversation_id=conversation_id,
        user=current_user,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=AssistantReply)
def create_message(
    business_id: UUID,
    conversation_id: UUID,
    payload: AssistantMessageCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> AssistantReply:
    return AssistantService(db).ask(
        business_id=business_id,
        conversation_id=conversation_id,
        payload=payload,
        user=current_user,
    )
