from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None


class ChatCitation(BaseModel):
    label: str
    source: str


class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    citations: list[ChatCitation] = []

