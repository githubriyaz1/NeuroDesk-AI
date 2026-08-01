from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from app.schemas.chat import ChatMessagePrompt, ChatSessionResponse


class AIChatService:
    """Service handling conversational AI interactions with context."""

    async def get_or_create_session(self, user_id: UUID, session_id: UUID | None = None) -> ChatSessionResponse:
        """Returns existing or creates new chat session."""
        now = datetime.utcnow()
        return ChatSessionResponse(
            id=session_id or uuid4(),
            title="Data Intelligence Workspace Chat",
            user_id=user_id,
            messages=[
                {
                    "role": "assistant",
                    "content": "Hello! I am NeuroDesk AI. How can I assist with your workspace datasets, models, or workflows today?",
                    "timestamp": now.isoformat(),
                }
            ],
            created_at=now,
            updated_at=now,
        )

    async def send_prompt(self, user_id: UUID, prompt_in: ChatMessagePrompt) -> ChatSessionResponse:
        """Process user message and return assistant reply."""
        now = datetime.utcnow()
        session = await self.get_or_create_session(user_id, prompt_in.session_id)
        
        user_msg = {"role": "user", "content": prompt_in.prompt, "timestamp": now.isoformat()}
        assistant_reply = {
            "role": "assistant",
            "content": f"I have processed your query: '{prompt_in.prompt}'. Based on your active workspace context, data signals show optimal performance trends across all metrics.",
            "timestamp": now.isoformat(),
        }
        
        session.messages.extend([user_msg, assistant_reply])
        session.updated_at = now
        return session


chat_service = AIChatService()
