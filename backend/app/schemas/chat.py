from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatMessagePrompt(BaseModel):
    session_id: Optional[UUID] = None
    prompt: str
    context_workspace_id: Optional[UUID] = None


class ChatSessionResponse(BaseModel):
    id: UUID
    title: str
    user_id: UUID
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
