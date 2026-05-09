from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.domain import Conversation, Message, User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai import AIOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    if payload.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == payload.conversation_id,
                Conversation.organization_id == user.organization_id,
                Conversation.user_id == user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            organization_id=user.organization_id,
            user_id=user.id,
            title=payload.message[:80],
        )
        db.add(conversation)
        await db.flush()

    db.add(Message(conversation_id=conversation.id, role="user", content=payload.message))
    answer, citations = await AIOrchestrator().answer(
        payload.message,
        {"organization_id": str(user.organization_id), "user_id": str(user.id)},
    )
    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            metadata_json={"citations": citations},
        )
    )
    await db.commit()
    return ChatResponse(conversation_id=conversation.id, answer=answer, citations=citations)
