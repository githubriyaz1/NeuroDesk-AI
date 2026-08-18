from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.llm.streaming import cancellation_manager, stream_cache
from app.core.logging import logger
from app.database.session import get_db
from app.models.user import User
from app.repositories.chat_repository import conversation_repo, message_repo
from app.routers.deps import get_current_active_user
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageUpdate,
    ConversationCreate,
    ConversationExportResponse,
    ConversationImportRequest,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    LLMDiagnosticsResponse,
    MessageListResponse,
)
from app.services.chat_service import chat_service
from app.services.llm_service import llm_service
from app.utils.response import success_response

router = APIRouter(prefix="/chat", tags=["AI Chat Platform"])


# Diagnostics & Health Endpoint
@router.get("/diagnostics", response_model=LLMDiagnosticsResponse)
async def get_chat_diagnostics(current_user: User = Depends(get_current_active_user)):
    """Returns streaming health, memory status, average latency, and cancellation metrics."""
    return llm_service.get_diagnostics()


# Real-time SSE Streaming Endpoint
@router.post("/stream")
async def stream_chat_response(
    msg_in: ChatMessageCreate,
    stream_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Streams live assistant responses using Server-Sent Events (SSE)."""
    # 1. Fetch or create conversation
    if not msg_in.conversation_id:
        title = chat_service.title_service.generate_title(msg_in.prompt)
        conv = await conversation_repo.create(db, current_user.id, {"title": title})
        conversation_id = conv.id
    else:
        conversation_id = msg_in.conversation_id
        conv = await conversation_repo.get_by_id(db, current_user.id, conversation_id)
        if not conv:
            return success_response(message="Conversation not found", status_code=404)

    # 2. Persist User Message
    user_msg = await message_repo.create_message(
        db,
        conversation_id,
        {
            "role": "user",
            "content": msg_in.prompt,
            "markdown": msg_in.prompt,
            "message_status": "completed",
        },
    )

    # 3. Create Placeholder Assistant Message
    assistant_msg = await message_repo.create_message(
        db,
        conversation_id,
        {
            "parent_message_id": user_msg.id,
            "role": "assistant",
            "content": "",
            "message_status": "streaming",
        },
    )

    history = await message_repo.list_messages(db, conversation_id)
    provider_info = conv.provider_info_json or {}
    raw_provider = provider_info.get("provider")
    is_explicit = provider_info.get("is_explicit", False)
    configured_provider = getattr(settings, "LLM_PROVIDER", "mock")

    if is_explicit and raw_provider:
        provider_name = raw_provider
    elif configured_provider and configured_provider != "mock":
        provider_name = configured_provider
    else:
        provider_name = raw_provider or configured_provider or "mock"

    # 4. Query Knowledge Engine for grounding context if available
    knowledge_context = None
    citations = None
    try:
        from app.core.knowledge.engine import knowledge_engine
        from app.schemas.knowledge import KnowledgeQueryRequest

        k_res = await knowledge_engine.query_knowledge(
            owner_id=current_user.id,
            req=KnowledgeQueryRequest(
                query=msg_in.prompt,
                asset_ids=msg_in.attached_assets if (msg_in.attached_assets and len(msg_in.attached_assets) > 0) else None,
                limit=3,
            ),
            db_session=db,
        )
        if k_res and k_res.citations:
            knowledge_context = k_res.packaged_context
            citations = [c.model_dump(mode="json") for c in k_res.citations]

        unique_kw = "NEURODESK_UNIQUE_84729"
        contains_kw = unique_kw in (knowledge_context or "")
        logger.info(
            f"[PDF_DEBUG]\n"
            f"query={msg_in.prompt}\n"
            f"attached_assets={msg_in.attached_assets}\n"
            f"retrieved_docs_count={len(citations) if citations else 0}\n"
            f"knowledge_context_length={len(knowledge_context) if knowledge_context else 0}\n"
            f"knowledge_context_contains_unique_keyword={contains_kw}\n"
            f"provider={provider_name}"
        )
    except Exception as exc:
        logger.warning(f"Knowledge Engine retrieval skipped for chat prompt: {exc}")

    return StreamingResponse(
        llm_service.stream_provider_response(
            conversation=conv,
            messages=history,
            current_prompt=msg_in.prompt,
            message_id=assistant_msg.id,
            provider_name=provider_name,
            stream_id=stream_id or str(uuid4()),
            knowledge_context=knowledge_context,
            citations=citations,
        ),
        media_type="text/event-stream; charset=utf-8",
    )


# Stream Control Endpoints
@router.post("/messages/{id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_message_stream(
    id: UUID,
    stream_id: str = Query(...),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel an active in-flight streaming LLM response."""
    cancellation_manager.request_cancellation(stream_id)
    return success_response(message=f"Stream cancellation requested for [{stream_id}]")


@router.get("/stream/{stream_id}/reconnect")
async def reconnect_stream(
    stream_id: str,
    last_chunk_index: int = Query(-1),
    current_user: User = Depends(get_current_active_user),
):
    """Replays missed SSE chunks for a stream following network disconnection."""
    chunks = stream_cache.get_chunks_since(stream_id, last_chunk_index)
    
    async def replay_generator():
        for chunk in chunks:
            yield f"data: {chunk.model_dump_json()}\n\n"

    return StreamingResponse(replay_generator(), media_type="text/event-stream")


@router.post("/messages/{id}/regenerate", response_model=ChatMessageResponse)
async def regenerate_message(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate assistant response for a given message."""
    target_msg = await message_repo.get_by_id(db, id)
    if not target_msg or target_msg.role != "assistant":
        return success_response(message="Invalid assistant message ID", status_code=400)

    # Fetch parent user prompt
    parent_msg = await message_repo.get_by_id(db, target_msg.parent_message_id)
    prompt = parent_msg.content if parent_msg else "Please summarize our progress."

    msg_in = ChatMessageCreate(conversation_id=target_msg.conversation_id, prompt=prompt)
    return await chat_service.post_user_message(db, current_user.id, msg_in)


# Standard Conversation Endpoints
@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_archived: Optional[bool] = Query(False),
    is_favorite: Optional[bool] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.list_conversations(
        db, current_user.id, page, page_size, is_archived, is_favorite, is_pinned, search
    )


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data_in: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.create_conversation(db, current_user.id, data_in)


@router.get("/conversations/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.get_conversation(db, current_user.id, id)


@router.patch("/conversations/{id}", response_model=ConversationResponse)
async def update_conversation(
    id: UUID,
    data_in: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.update_conversation(db, current_user.id, id, data_in)


@router.delete("/conversations/{id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await chat_service.delete_conversation(db, current_user.id, id)
    return success_response(message="Conversation deleted successfully")


@router.post("/conversations/{id}/archive", response_model=ConversationResponse)
async def archive_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.toggle_flag(db, current_user.id, id, "archive")


@router.post("/conversations/{id}/favorite", response_model=ConversationResponse)
async def favorite_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.toggle_flag(db, current_user.id, id, "favorite")


@router.post("/conversations/{id}/pin", response_model=ConversationResponse)
async def pin_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.toggle_flag(db, current_user.id, id, "pin")


@router.post("/conversations/{id}/duplicate", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.duplicate_conversation(db, current_user.id, id)


@router.post("/conversations/{id}/restore", response_model=ConversationResponse)
async def restore_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.restore_conversation(db, current_user.id, id)


@router.post("/conversations/{id}/clear", response_model=ConversationResponse)
async def clear_conversation(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.clear_conversation(db, current_user.id, id)


@router.get("/conversations/{id}/export", response_model=ConversationExportResponse)
async def export_conversation(
    id: UUID,
    format: str = Query("markdown", pattern="^(markdown|json)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.export_conversation(db, current_user.id, id, format)


@router.post("/conversations/import", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def import_conversation(
    req: ConversationImportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.import_conversation(db, current_user.id, req.json_content)


# Message Endpoints
@router.get("/messages/{conversation_id}", response_model=MessageListResponse)
async def get_messages(
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    messages = await chat_service.get_messages(db, current_user.id, conversation_id)
    return MessageListResponse(
        conversation_id=conversation_id,
        messages=messages,
        total=len(messages),
    )


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def post_message(
    msg_in: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.post_user_message(db, current_user.id, msg_in)


@router.patch("/messages/{id}", response_model=ChatMessageResponse)
async def update_message(
    id: UUID,
    data_in: ChatMessageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    return await chat_service.update_message(db, current_user.id, id, data_in.content)


@router.delete("/messages/{id}", status_code=status.HTTP_200_OK)
async def delete_message(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await chat_service.delete_message(db, current_user.id, id)
    return success_response(message="Message deleted successfully")
