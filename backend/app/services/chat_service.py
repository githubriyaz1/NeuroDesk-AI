import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis import analysis_engine
from app.core.knowledge import knowledge_engine
from app.core.config import settings
from app.core.llm.base import ProviderRequest
from app.core.logging import logger
from app.core.project_generator import project_generation_engine
from app.models.chat import Conversation, ChatMessage, MessageRole, MessageStatus
from app.repositories.chat_repository import conversation_repo, message_repo
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ConversationCreate,
    ConversationExportResponse,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
)
from app.schemas.knowledge import KnowledgeQueryRequest
from app.services.llm_service import llm_service


def to_conversation_dto(conv: Conversation) -> ConversationResponse:
    """Safely build ConversationResponse DTO, checking SQLAlchemy attribute loading state."""
    state = inspect(conv)
    messages_dto = None
    if "messages" not in state.unloaded and conv.messages is not None:
        messages_dto = [ChatMessageResponse.model_validate(m) for m in conv.messages]

    return ConversationResponse(
        id=conv.id,
        owner_id=conv.owner_id,
        title=conv.title,
        description=conv.description,
        summary=conv.summary,
        folder_id=getattr(conv, "folder_id", None),
        message_count=conv.message_count,
        total_token_usage=conv.total_token_usage or {},
        estimated_cost=conv.estimated_cost,
        is_pinned=conv.is_pinned,
        is_favorite=conv.is_favorite,
        is_archived=conv.is_archived,
        future_tags=conv.future_tags or [],
        settings_json=conv.settings_json or {},
        provider_info_json=conv.provider_info_json or {},
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        last_message_at=conv.last_message_at,
        messages=messages_dto,
    )


class ConversationTitleService:
    """Deterministic title generation from initial user prompt."""

    @staticmethod
    def generate_title(first_prompt: str) -> str:
        clean = first_prompt.strip().replace("\n", " ")
        if not clean:
            return "New Conversation"
        
        words = clean.split(" ")
        title = " ".join(words[:6])
        if len(words) > 6:
            title += "..."
        return title[:60].capitalize()


class ConversationExportService:
    """Export conversation into Markdown or JSON format."""

    @staticmethod
    def export_conversation(conversation: Conversation, format_type: str) -> str:
        if format_type.lower() == "json":
            export_data = {
                "id": str(conversation.id),
                "title": conversation.title,
                "description": conversation.description,
                "created_at": conversation.created_at.isoformat(),
                "messages": [
                    {
                        "id": str(m.id),
                        "role": m.role,
                        "content": m.content,
                        "created_at": m.created_at.isoformat(),
                        "attachments": m.attachments,
                    }
                    for m in conversation.messages
                ],
            }
            return json.dumps(export_data, indent=2)

        # Default Markdown format
        md_lines = [
            f"# {conversation.title}",
            f"**Exported**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Total Messages**: {conversation.message_count}",
            "\n---\n",
        ]
        for msg in conversation.messages:
            role_badge = "**User**" if msg.role == "user" else "**Assistant**"
            md_lines.append(f"### {role_badge} ({msg.created_at.strftime('%H:%M:%S')})\n")
            md_lines.append(f"{msg.content}\n")
            md_lines.append("\n---\n")

        return "\n".join(md_lines)


class ConversationImportService:
    """Import conversation from JSON structure."""

    @staticmethod
    async def import_conversation(db: AsyncSession, owner_id: UUID, json_payload: Dict[str, Any]) -> Conversation:
        title = json_payload.get("title", "Imported Conversation")
        description = json_payload.get("description", "Imported from external backup")
        
        conv_data = {"title": title, "description": description}
        conversation = await conversation_repo.create(db, owner_id, conv_data)

        raw_messages = json_payload.get("messages", [])
        for raw_msg in raw_messages:
            msg_data = {
                "role": raw_msg.get("role", MessageRole.USER.value),
                "content": raw_msg.get("content", ""),
                "attachments": raw_msg.get("attachments", []),
            }
            await message_repo.create_message(db, conversation.id, msg_data)

        return conversation


class AIChatService:
    """Comprehensive Enterprise Service orchestrating Conversations, Messages, and AI Platform Engine integrations."""

    def __init__(self):
        self.title_service = ConversationTitleService()
        self.export_service = ConversationExportService()
        self.import_service = ConversationImportService()

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
    ) -> ConversationListResponse:
        items, total = await conversation_repo.list_conversations(
            db, owner_id, page, page_size, is_archived, is_favorite, is_pinned, search
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        conv_dtos = [to_conversation_dto(c) for c in items]
        return ConversationListResponse(
            items=conv_dtos,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_conversation(self, db: AsyncSession, owner_id: UUID, data_in: ConversationCreate) -> ConversationResponse:
        title = data_in.title or "New Conversation"
        configured_provider = getattr(settings, "LLM_PROVIDER", "mock")
        configured_model = (
            getattr(settings, "LLM_MODEL", "gemini-2.5-flash")
            if configured_provider == "gemini"
            else "neurodesk-mock-v1"
        )
        default_settings = {
            "model": configured_model,
            "temperature": 0.7,
            "max_tokens": 4096,
            "system_prompt": "You are NeuroDesk AI, an intelligent workspace assistant.",
        }
        default_provider_info = {
            "provider": configured_provider,
            "api_version": "v1",
            "is_explicit": False,
        }
        conv_data = {
            "title": title,
            "description": data_in.description,
            "settings_json": data_in.settings_json or default_settings,
            "provider_info_json": getattr(data_in, "provider_info_json", None) or default_provider_info,
        }
        conversation = await conversation_repo.create(db, owner_id, conv_data)
        logger.info(f"Created new conversation '{conversation.title}' [{conversation.id}] for user [{owner_id}]")
        return to_conversation_dto(conversation)

    async def get_conversation(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> ConversationResponse:
        conversation = await conversation_repo.get_by_id(db, owner_id, conversation_id, include_messages=True)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )
        return to_conversation_dto(conversation)

    async def update_conversation(
        self, db: AsyncSession, owner_id: UUID, conversation_id: UUID, data_in: ConversationUpdate
    ) -> ConversationResponse:
        conversation = await conversation_repo.get_by_id(db, owner_id, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )

        updates = data_in.model_dump(exclude_unset=True)
        updated = await conversation_repo.update(db, conversation, updates)
        logger.info(f"Updated conversation [{conversation_id}] for user [{owner_id}]")
        return to_conversation_dto(updated)

    async def delete_conversation(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> None:
        deleted = await conversation_repo.delete(db, owner_id, conversation_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )
        logger.info(f"Deleted conversation [{conversation_id}]")

    async def toggle_flag(
        self, db: AsyncSession, owner_id: UUID, conversation_id: UUID, flag_type: str, state: Optional[bool] = None
    ) -> ConversationResponse:
        conversation = await conversation_repo.get_by_id(db, owner_id, conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )

        if flag_type == "archive":
            new_val = not conversation.is_archived if state is None else state
            conversation = await conversation_repo.update(db, conversation, {"is_archived": new_val})
        elif flag_type == "favorite":
            new_val = not conversation.is_favorite if state is None else state
            conversation = await conversation_repo.update(db, conversation, {"is_favorite": new_val})
        elif flag_type == "pin":
            new_val = not conversation.is_pinned if state is None else state
            conversation = await conversation_repo.update(db, conversation, {"is_pinned": new_val})

        return to_conversation_dto(conversation)

    async def duplicate_conversation(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> ConversationResponse:
        dup = await conversation_repo.duplicate(db, owner_id, conversation_id)
        if not dup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )
        return to_conversation_dto(dup)

    async def restore_conversation(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> ConversationResponse:
        return await self.toggle_flag(db, owner_id, conversation_id, "archive", state=False)

    async def clear_conversation(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> ConversationResponse:
        cleared = await conversation_repo.clear_messages(db, owner_id, conversation_id)
        if not cleared:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )
        return await self.get_conversation(db, owner_id, conversation_id)

    async def export_conversation(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID, format_type: str) -> ConversationExportResponse:
        conversation = await conversation_repo.get_by_id(db, owner_id, conversation_id, include_messages=True)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )

        content = self.export_service.export_conversation(conversation, format_type)
        return ConversationExportResponse(
            conversation_id=conversation.id,
            title=conversation.title,
            format=format_type,
            content=content,
            exported_at=datetime.now(timezone.utc),
        )

    async def import_conversation(self, db: AsyncSession, owner_id: UUID, json_payload: Dict[str, Any]) -> ConversationResponse:
        conversation = await self.import_service.import_conversation(db, owner_id, json_payload)
        return await self.get_conversation(db, owner_id, conversation.id)

    # Message Operations & AI Platform Module Integrations
    async def get_messages(self, db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> List[ChatMessageResponse]:
        conv = await conversation_repo.get_by_id(db, owner_id, conversation_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied.",
            )
        messages = await message_repo.list_messages(db, conversation_id)
        return [ChatMessageResponse.model_validate(m) for m in messages]

    async def post_user_message(self, db: AsyncSession, owner_id: UUID, msg_in: ChatMessageCreate) -> ChatMessageResponse:
        # Create or fetch conversation
        if not msg_in.conversation_id:
            title = self.title_service.generate_title(msg_in.prompt)
            conv = await conversation_repo.create(db, owner_id, {"title": title})
            conversation_id = conv.id
        else:
            conversation_id = msg_in.conversation_id
            conv = await conversation_repo.get_by_id(db, owner_id, conversation_id)
            if not conv:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or access denied.",
                )

        # Save User Message
        user_msg_data = {
            "role": MessageRole.USER.value,
            "content": msg_in.prompt,
            "markdown": msg_in.prompt,
            "attachments": msg_in.attachments,
            "attached_assets": [str(a) for a in msg_in.attached_assets],
            "mentioned_assets": [str(a) for a in msg_in.mentioned_assets],
            "message_status": MessageStatus.COMPLETED.value,
        }
        user_msg = await message_repo.create_message(db, conversation_id, user_msg_data)

        prompt_lower = msg_in.prompt.lower().strip()
        all_assets = list(set(msg_in.attached_assets + msg_in.mentioned_assets))

        # -------------------------------------------------------------------
        # INTENT INTEGRATION 1: Project Generator
        # If user requests generating a project or architecture
        # -------------------------------------------------------------------
        if any(kw in prompt_lower for kw in ["generate a project", "build architecture", "generate project", "generate blueprint"]):
            try:
                blueprint_data = await project_generation_engine.generate_project(
                    db=db,
                    owner_id=owner_id,
                    title="Project Blueprint from Chat",
                    description=msg_in.prompt,
                    include_knowledge_context=True,
                    asset_ids=all_assets if all_assets else None,
                )
                summary = blueprint_data.get("summary", {})
                reqs = blueprint_data.get("requirements", {})
                t_stack = blueprint_data.get("tech_stack", {})
                
                content_md = f"### 🚀 Generated Project Blueprint: {summary.get('title')}\n\n"
                content_md += f"**Description**: {summary.get('description')}\n\n"
                content_md += f"**Primary Stack**: {t_stack.get('recommended_primary', {}).get('frontend')} + {t_stack.get('recommended_primary', {}).get('backend')} + {t_stack.get('recommended_primary', {}).get('database')}\n\n"
                content_md += f"**Problem Statement**: {reqs.get('problem_statement')}\n\n"
                content_md += "#### Key Objectives:\n"
                for obj in reqs.get("objectives", []):
                    content_md += f"- {obj}\n"

                assistant_msg_data = {
                    "parent_message_id": user_msg.id,
                    "role": MessageRole.ASSISTANT.value,
                    "content": content_md,
                    "markdown": content_md,
                    "retrieved_assets": [str(a) for a in all_assets],
                    "metadata_info": {"blueprint_generated": True, "project_type": summary.get("project_type")},
                    "message_status": MessageStatus.COMPLETED.value,
                }
                assistant_msg = await message_repo.create_message(db, conversation_id, assistant_msg_data)
                return ChatMessageResponse.model_validate(assistant_msg)
            except Exception as err:
                logger.error(f"Project Generator intent execution error: {err}")

        # -------------------------------------------------------------------
        # INTENT INTEGRATION 2: Analysis Engine
        # If user requests analyzing document, dataset, or comparing
        # -------------------------------------------------------------------
        if any(kw in prompt_lower for kw in ["analyze this document", "summarize this dataset", "compare these two pdfs", "analyze asset"]):
            try:
                # Run document or dataset analysis
                doc_analysis = analysis_engine.doc_analyzer.analyze_document(
                    asset_id=all_assets[0] if all_assets else UUID("00000000-0000-0000-0000-000000000000"),
                    filename="Attached_Asset.pdf",
                    mime_type="application/pdf",
                    text_content=f"Document analysis content for: {msg_in.prompt}",
                )
                
                content_md = f"### 📊 Analysis Engine Report\n\n"
                content_md += f"**Summary**: {doc_analysis.summary}\n\n"
                content_md += f"**Word Count**: {doc_analysis.word_count} | **Readability Score**: {doc_analysis.readability_score}\n\n"
                content_md += "#### Key Insights:\n"
                for ins in doc_analysis.key_insights:
                    content_md += f"- **[{ins.category}]**: {ins.text}\n"

                assistant_msg_data = {
                    "parent_message_id": user_msg.id,
                    "role": MessageRole.ASSISTANT.value,
                    "content": content_md,
                    "markdown": content_md,
                    "retrieved_assets": [str(a) for a in all_assets],
                    "metadata_info": {"analysis_completed": True},
                    "message_status": MessageStatus.COMPLETED.value,
                }
                assistant_msg = await message_repo.create_message(db, conversation_id, assistant_msg_data)
                return ChatMessageResponse.model_validate(assistant_msg)
            except Exception as err:
                logger.error(f"Analysis Engine intent execution error: {err}")

        # -------------------------------------------------------------------
        # INTENT INTEGRATION 3: Knowledge Engine
        # Query RAG citations when prompt asks about uploaded docs or assets attached
        # -------------------------------------------------------------------
        context_block = ""
        citations = []
        if all_assets or any(kw in prompt_lower for kw in ["what is inside", "find apis", "my uploaded documents", "in my specs"]):
            try:
                k_req = KnowledgeQueryRequest(query=msg_in.prompt, limit=5, asset_ids=all_assets if all_assets else None)
                kq_res = await knowledge_engine.query_knowledge(owner_id=owner_id, req=k_req, db_session=db)
                citations = [c.model_dump() for c in kq_res.citations]
                context_block = kq_res.packaged_context or ""
            except Exception as err:
                logger.error(f"Knowledge Engine query error: {err}")

        # -------------------------------------------------------------------
        # Standard LLM Provider Invocation
        # -------------------------------------------------------------------
        provider_info = conv.provider_info_json or {}
        provider_name = provider_info.get("provider", "mock")
        settings = conv.settings_json or {}

        augmented_prompt = msg_in.prompt
        if context_block:
            augmented_prompt = f"Knowledge Context:\n{context_block}\n\nUser Question: {msg_in.prompt}"

        req = ProviderRequest(
            prompt=augmented_prompt,
            system_prompt=settings.get("system_prompt"),
            model=settings.get("model", "neurodesk-mock-v1"),
            temperature=settings.get("temperature", 0.7),
            max_tokens=settings.get("max_tokens", 4096),
        )

        try:
            llm_response = await llm_service.execute_provider_request(provider_name, req)
            assistant_msg_data = {
                "parent_message_id": user_msg.id,
                "role": MessageRole.ASSISTANT.value,
                "content": llm_response.content,
                "markdown": llm_response.markdown_content or llm_response.content,
                "token_usage": llm_response.token_usage.model_dump(),
                "latency_ms": llm_response.latency_ms,
                "retrieved_assets": [str(a) for a in all_assets],
                "metadata_info": {"citations": citations, **llm_response.metadata},
                "message_status": MessageStatus.COMPLETED.value,
            }
            assistant_msg = await message_repo.create_message(db, conversation_id, assistant_msg_data)

            # Auto-update conversation title if still default "New Conversation"
            if conv.title == "New Conversation":
                auto_title = self.title_service.generate_title(msg_in.prompt)
                await conversation_repo.update(db, conv, {"title": auto_title})

            # Update conversation cumulative usage & estimated cost
            current_usage = conv.total_token_usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            p_tokens = current_usage.get("prompt_tokens", 0) + llm_response.token_usage.prompt_tokens
            c_tokens = current_usage.get("completion_tokens", 0) + llm_response.token_usage.completion_tokens
            new_usage = {
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "total_tokens": p_tokens + c_tokens,
            }
            cost = llm_service.estimate_cost(p_tokens, c_tokens, provider_name)
            await conversation_repo.update(db, conv, {"total_token_usage": new_usage, "estimated_cost": cost})

            logger.info(f"Generated assistant message for conversation [{conversation_id}] via {provider_name}")
            return ChatMessageResponse.model_validate(assistant_msg)

        except Exception as exc:
            logger.error(f"Error during LLM provider generation: {exc}")
            err_msg_data = {
                "parent_message_id": user_msg.id,
                "role": MessageRole.ERROR.value,
                "content": f"An error occurred while generating response: {str(exc)}",
                "message_status": MessageStatus.FAILED.value,
            }
            err_msg = await message_repo.create_message(db, conversation_id, err_msg_data)
            return ChatMessageResponse.model_validate(err_msg)

    async def update_message(self, db: AsyncSession, owner_id: UUID, message_id: UUID, new_content: str) -> ChatMessageResponse:
        msg = await message_repo.get_by_id(db, message_id)
        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found.",
            )

        conv = await conversation_repo.get_by_id(db, owner_id, msg.conversation_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this message.",
            )

        updated_msg = await message_repo.update_message(db, msg, new_content)
        return ChatMessageResponse.model_validate(updated_msg)

    async def delete_message(self, db: AsyncSession, owner_id: UUID, message_id: UUID) -> None:
        msg = await message_repo.get_by_id(db, message_id)
        if not msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found.",
            )

        conv = await conversation_repo.get_by_id(db, owner_id, msg.conversation_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this message.",
            )

        await message_repo.delete_message(db, message_id)


chat_service = AIChatService()
