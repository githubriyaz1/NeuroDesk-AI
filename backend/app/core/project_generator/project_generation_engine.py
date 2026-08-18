from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis import analysis_engine
from app.core.knowledge import knowledge_engine
from app.core.project_generator.blueprint_engine import blueprint_engine
from app.schemas.knowledge import KnowledgeQueryRequest
from app.services.llm_service import llm_service


class ProjectGenerationEngine:
    """Facade integrating KnowledgeEngine, AnalysisEngine, WorkflowEngine, and LLMService into blueprint generation."""

    def __init__(self):
        self.blueprint_eng = blueprint_engine
        self.knowledge_eng = knowledge_engine
        self.analysis_eng = analysis_engine
        self.llm_service = llm_service

    async def generate_project(
        self,
        db: AsyncSession,
        owner_id: UUID,
        title: str,
        description: str,
        project_type: str = "web_app",
        preferred_tech_stack: Optional[List[str]] = None,
        include_knowledge_context: bool = True,
        asset_ids: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        context_knowledge = {}

        # 1. Knowledge Engine Integration: retrieve contextual assets (resumes, API docs, papers)
        if include_knowledge_context:
            try:
                req = KnowledgeQueryRequest(
                    query=f"Architectural design and technical requirements for {title}: {description}",
                    limit=5,
                    asset_ids=asset_ids,
                )
                kq = await self.knowledge_eng.query_knowledge(
                    owner_id=owner_id,
                    req=req,
                    db_session=db,
                )
                context_knowledge = {
                    "citations_count": len(kq.citations),
                    "retrieved_context": kq.packaged_context[:1000] if kq.packaged_context else "",
                    "citations": [c.model_dump(mode="json") for c in kq.citations],
                }
            except Exception as err:
                context_knowledge = {"error": f"Knowledge engine context skipped: {str(err)}"}

        # 2. Assemble full project blueprint
        blueprint_payload = self.blueprint_eng.assemble_blueprint(
            title=title,
            description=description,
            project_type=project_type,
            preferred_tech_stack=preferred_tech_stack,
            context_knowledge=context_knowledge,
        )

        # 3. Optional LLM Service Enhancement
        try:
            llm_summary = await self.llm_service.generate_non_streaming(
                provider_name="mock",
                model_name="neurodesk-mock-v1",
                prompt=f"Provide an architectural summary for {title} ({project_type}): {description}",
                system_instruction="You are a Principal Software Architect.",
            )
            blueprint_payload["summary"]["ai_architect_notes"] = llm_summary.get("text", "")
        except Exception:
            blueprint_payload["summary"]["ai_architect_notes"] = f"Enterprise blueprint generated for {title}."

        return blueprint_payload


project_generation_engine = ProjectGenerationEngine()
