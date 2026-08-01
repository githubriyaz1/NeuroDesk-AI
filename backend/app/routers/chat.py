from uuid import UUID
from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.chat import ChatMessagePrompt, ChatSessionResponse
from app.services.chat_service import chat_service
from app.routers.deps import get_current_active_user

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("/prompt", response_model=ChatSessionResponse)
async def prompt_chat(
    prompt_in: ChatMessagePrompt,
    current_user: User = Depends(get_current_active_user),
):
    """Send conversational prompt to AI workspace assistant."""
    return await chat_service.send_prompt(user_id=current_user.id, prompt_in=prompt_in)


@router.get("/session", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: UUID | None = None,
    current_user: User = Depends(get_current_active_user),
):
    """Get active chat session history."""
    return await chat_service.get_or_create_session(user_id=current_user.id, session_id=session_id)
