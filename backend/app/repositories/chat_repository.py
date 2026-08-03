from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Conversation, ChatMessage, MessageRole, MessageStatus
from app.core.logging import logger


class ConversationRepository:
    """Enterprise DB Repository for Conversation entities with strict tenant isolation."""

    async def create(self, db: AsyncSession, owner_id: UUID, conversation_data: Dict[str, Any]) -> Conversation:
        now = datetime.now(timezone.utc)
        conversation = Conversation(
            id=uuid4(),
            owner_id=owner_id,
            title=conversation_data.get("title", "New Conversation"),
            description=conversation_data.get("description"),
            summary=conversation_data.get("summary"),
            settings_json=conversation_data.get(
                "settings_json",
                {
                    "model": "neurodesk-mock-v1",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "system_prompt": "You are NeuroDesk AI, an intelligent workspace assistant.",
                },
            ),
            created_at=now,
            updated_at=now,
            last_message_at=now,
        )
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation

    async def get_by_id(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID, include_messages: bool = False) -> Optional[Conversation]:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.owner_id == owner_id,
        )
        if include_messages:
            stmt = stmt.options(selectinload(Conversation.messages))
            
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_conversations(
        self,
        db: AsyncSession,
        owner_id: UUID,
        page: int = 1,
        page_size: int = 20,
        is_archived: Optional[bool] = False,
        is_favorite: Optional[bool] = None,
        is_pinned: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Conversation], int]:
        stmt = select(Conversation).where(Conversation.owner_id == owner_id)

        if is_archived is not None:
            stmt = stmt.where(Conversation.is_archived == is_archived)
        if is_favorite is not None:
            stmt = stmt.where(Conversation.is_favorite == is_favorite)
        if is_pinned is not None:
            stmt = stmt.where(Conversation.is_pinned == is_pinned)

        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Conversation.title).like(pattern),
                    func.lower(Conversation.description).like(pattern),
                    func.lower(Conversation.summary).like(pattern),
                )
            )

        # Count total items
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Pagination & Sorting (Pinned first, then last_message_at desc)
        stmt = (
            stmt.order_by(Conversation.is_pinned.desc(), Conversation.last_message_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def update(self, db: AsyncSession, conversation: Conversation, updates: Dict[str, Any]) -> Conversation:
        now = datetime.now(timezone.utc)
        for key, val in updates.items():
            if val is not None and hasattr(conversation, key):
                setattr(conversation, key, val)
        
        conversation.updated_at = now
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation

    async def delete(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> bool:
        stmt = delete(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.owner_id == owner_id,
        )
        res = await db.execute(stmt)
        return res.rowcount > 0

    async def duplicate(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> Optional[Conversation]:
        source = await self.get_by_id(db, owner_id, conversation_id, include_messages=True)
        if not source:
            return None

        now = datetime.now(timezone.utc)
        dup_conversation = Conversation(
            id=uuid4(),
            owner_id=owner_id,
            title=f"{source.title} (Copy)",
            description=source.description,
            summary=source.summary,
            settings_json=dict(source.settings_json or {}),
            created_at=now,
            updated_at=now,
            last_message_at=now,
        )
        db.add(dup_conversation)
        await db.flush()

        # Copy all messages
        copied_msg_count = 0
        for msg in source.messages:
            new_msg = ChatMessage(
                id=uuid4(),
                conversation_id=dup_conversation.id,
                role=msg.role,
                content=msg.content,
                markdown=msg.markdown,
                attachments=list(msg.attachments or []),
                attached_assets=list(msg.attached_assets or []),
                mentioned_assets=list(msg.mentioned_assets or []),
                retrieved_assets=list(msg.retrieved_assets or []),
                token_usage=dict(msg.token_usage or {}),
                latency_ms=msg.latency_ms,
                message_status=msg.message_status,
                created_at=now,
                updated_at=now,
            )
            db.add(new_msg)
            copied_msg_count += 1

        dup_conversation.message_count = copied_msg_count
        db.add(dup_conversation)
        await db.flush()
        await db.refresh(dup_conversation)
        return dup_conversation

    async def clear_messages(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> bool:
        conv = await self.get_by_id(db, owner_id, conversation_id)
        if not conv:
            return False

        del_stmt = delete(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
        await db.execute(del_stmt)

        conv.message_count = 0
        conv.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        conv.updated_at = datetime.now(timezone.utc)
        db.add(conv)
        await db.flush()
        return True


class MessageRepository:
    """Enterprise DB Repository for ChatMessage entities."""

    async def create_message(self, db: AsyncSession, conversation_id: UUID, message_data: Dict[str, Any]) -> ChatMessage:
        now = datetime.now(timezone.utc)
        msg = ChatMessage(
            id=uuid4(),
            conversation_id=conversation_id,
            parent_message_id=message_data.get("parent_message_id"),
            role=message_data.get("role", MessageRole.USER.value),
            content=message_data.get("content", ""),
            markdown=message_data.get("markdown", message_data.get("content", "")),
            attachments=message_data.get("attachments", []),
            attached_assets=message_data.get("attached_assets", []),
            mentioned_assets=message_data.get("mentioned_assets", []),
            retrieved_assets=message_data.get("retrieved_assets", []),
            token_usage=message_data.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
            latency_ms=message_data.get("latency_ms", 0.0),
            metadata_info=message_data.get("metadata_info", {}),
            message_status=message_data.get("message_status", MessageStatus.COMPLETED.value),
            created_at=now,
            updated_at=now,
        )
        db.add(msg)
        await db.flush()
        
        # Update conversation message_count and last_message_at
        stmt = update(Conversation).where(Conversation.id == conversation_id).values(
            message_count=Conversation.message_count + 1,
            last_message_at=now,
            updated_at=now,
        )
        await db.execute(stmt)
        await db.refresh(msg)
        return msg

    async def get_by_id(self, db: AsyncSession, message_id: UUID) -> Optional[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.id == message_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_messages(self, db: AsyncSession, conversation_id: UUID) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def update_message(self, db: AsyncSession, message: ChatMessage, new_content: str) -> ChatMessage:
        now = datetime.now(timezone.utc)
        message.content = new_content
        message.markdown = new_content
        message.is_edited = True
        message.version += 1
        message.updated_at = now
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message

    async def delete_message(self, db: AsyncSession, message_id: UUID) -> bool:
        stmt = delete(ChatMessage).where(ChatMessage.id == message_id)
        res = await db.execute(stmt)
        return res.rowcount > 0


conversation_repo = ConversationRepository()
message_repo = MessageRepository()
