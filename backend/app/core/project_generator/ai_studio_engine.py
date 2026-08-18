from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.project_generator.export_engine import export_engine
from app.core.project_generator.project_generation_engine import project_generation_engine


class AIStudioEngine:
    """Primary facade for AI Studio & Intelligent Project Generator."""

    def __init__(self):
        self.generator = project_generation_engine
        self.exporter = export_engine

    async def generate_blueprint(
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
        return await self.generator.generate_project(
            db=db,
            owner_id=owner_id,
            title=title,
            description=description,
            project_type=project_type,
            preferred_tech_stack=preferred_tech_stack,
            include_knowledge_context=include_knowledge_context,
            asset_ids=asset_ids,
        )

    def export_blueprint_document(self, blueprint_data: Dict[str, Any], fmt: str = "markdown") -> Dict[str, str]:
        return self.exporter.export_blueprint(blueprint_data, fmt)

    def get_starter_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "template-saas-platform",
                "name": "Enterprise Multi-Tenant SaaS Platform",
                "description": "Full-stack SaaS workspace with RBAC, billing, PostgreSQL, and React frontend.",
                "project_type": "saas_platform",
                "tech_stack": {
                    "frontend_frameworks": ["React", "Next.js", "Tailwind CSS"],
                    "backend_frameworks": ["FastAPI (Python)"],
                    "databases": ["PostgreSQL", "Redis"],
                    "devops_infrastructure": ["Docker", "Kubernetes"],
                },
                "architecture": {"pattern": "4-Tier Layered Architecture"},
                "requirements": {"objectives": ["Multi-tenant isolation", "99.9% uptime", "Sub-200ms API response"]},
            },
            {
                "id": "template-rag-ai-app",
                "name": "Intelligent RAG AI Knowledge Search",
                "description": "Enterprise RAG platform integrating vector retrieval, citations, and LLMs.",
                "project_type": "ai_app",
                "tech_stack": {
                    "frontend_frameworks": ["React", "Tailwind CSS"],
                    "backend_frameworks": ["FastAPI", "LangChain"],
                    "databases": ["PostgreSQL (pgvector)", "Redis"],
                    "devops_infrastructure": ["Docker"],
                },
                "architecture": {"pattern": "Microservices AI Retrieval Pattern"},
                "requirements": {"objectives": ["Parallel retriever execution", "Citation grounding"]},
            },
        ]


ai_studio_engine = AIStudioEngine()
