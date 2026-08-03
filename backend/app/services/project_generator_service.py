from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.project_generator import ai_studio_engine
from app.models.project_generator import BlueprintVersion, ProjectBlueprint, ProjectType
from app.repositories.project_generator_repository import project_generator_repository
from app.schemas.project_generator import (
    BlueprintUpdateRequest,
    ExportRequest,
    ProjectBlueprintResponse,
    ProjectGenerationRequest,
    ProjectMetricsResponse,
    ProjectTemplateResponse,
)


class ProjectGeneratorService:
    """Service layer managing AI Studio project blueprint generation, persistence, and version control."""

    def __init__(self):
        self.engine = ai_studio_engine
        self.repo = project_generator_repository

    async def generate_blueprint(
        self, db: AsyncSession, owner_id: UUID, req: ProjectGenerationRequest
    ) -> ProjectBlueprint:
        """Generates a comprehensive AI Studio project blueprint from plain English prompt."""
        blueprint_json = await self.engine.generate_blueprint(
            db=db,
            owner_id=owner_id,
            title=req.title,
            description=req.description,
            project_type=req.project_type,
            preferred_tech_stack=req.preferred_tech_stack,
            include_knowledge_context=req.include_knowledge_context,
            asset_ids=req.asset_ids,
        )

        blueprint_model = ProjectBlueprint(
            owner_id=owner_id,
            name=req.title,
            description=req.description,
            project_type=req.project_type,
            is_template=False,
            version=1,
            blueprint_json=blueprint_json,
            tech_stack_json=blueprint_json.get("tech_stack", {}),
            architecture_json=blueprint_json.get("architecture", {}),
            requirements_json=blueprint_json.get("requirements", {}),
            database_schema_json=blueprint_json.get("database_schema", {}),
            api_contracts_json=blueprint_json.get("api_contracts", {}),
            folder_tree_json=blueprint_json.get("folder_tree", {}),
            roadmap_json=blueprint_json.get("roadmap", {}),
        )

        created = await self.repo.create_blueprint(db, blueprint_model)

        # Snapshot version 1
        initial_version = BlueprintVersion(
            blueprint_id=created.id,
            version_number=1,
            blueprint_json=blueprint_json,
            changelog="Initial blueprint generation",
        )
        await self.repo.create_version(db, initial_version)

        return created

    async def get_blueprint(
        self, db: AsyncSession, owner_id: UUID, blueprint_id: UUID
    ) -> ProjectBlueprint:
        blueprint = await self.repo.get_blueprint_by_id(db, owner_id, blueprint_id)
        if not blueprint:
            raise ValueError(f"Project Blueprint '{blueprint_id}' not found.")
        return blueprint

    async def list_blueprints(
        self,
        db: AsyncSession,
        owner_id: UUID,
        page: int = 1,
        page_size: int = 20,
        project_type: Optional[str] = None,
    ) -> List[ProjectBlueprint]:
        blueprints, _ = await self.repo.list_blueprints(
            db, owner_id, page=page, page_size=page_size, project_type=project_type
        )
        return blueprints

    async def update_blueprint(
        self, db: AsyncSession, owner_id: UUID, blueprint_id: UUID, payload: BlueprintUpdateRequest
    ) -> ProjectBlueprint:
        blueprint = await self.get_blueprint(db, owner_id, blueprint_id)

        if payload.name is not None:
            blueprint.name = payload.name
        if payload.description is not None:
            blueprint.description = payload.description
        if payload.requirements is not None:
            blueprint.requirements_json = payload.requirements
            blueprint.blueprint_json["requirements"] = payload.requirements
        if payload.architecture is not None:
            blueprint.architecture_json = payload.architecture
            blueprint.blueprint_json["architecture"] = payload.architecture
        if payload.tech_stack is not None:
            blueprint.tech_stack_json = payload.tech_stack
            blueprint.blueprint_json["tech_stack"] = payload.tech_stack
        if payload.database_schema is not None:
            blueprint.database_schema_json = payload.database_schema
            blueprint.blueprint_json["database_schema"] = payload.database_schema
        if payload.api_contracts is not None:
            blueprint.api_contracts_json = payload.api_contracts
            blueprint.blueprint_json["api_contracts"] = payload.api_contracts
        if payload.folder_tree is not None:
            blueprint.folder_tree_json = payload.folder_tree
            blueprint.blueprint_json["folder_tree"] = payload.folder_tree
        if payload.roadmap is not None:
            blueprint.roadmap_json = payload.roadmap
            blueprint.blueprint_json["roadmap"] = payload.roadmap

        blueprint.version += 1
        saved = await self.repo.save_blueprint(db, blueprint)

        # Create version snapshot
        v_snap = BlueprintVersion(
            blueprint_id=saved.id,
            version_number=saved.version,
            blueprint_json=saved.blueprint_json,
            changelog=f"Updated to version {saved.version}",
        )
        await self.repo.create_version(db, v_snap)

        return saved

    async def clone_blueprint(
        self, db: AsyncSession, owner_id: UUID, blueprint_id: UUID
    ) -> ProjectBlueprint:
        original = await self.get_blueprint(db, owner_id, blueprint_id)
        cloned = ProjectBlueprint(
            owner_id=owner_id,
            name=f"{original.name} (Copy)",
            description=original.description,
            project_type=original.project_type,
            is_template=False,
            version=1,
            blueprint_json=original.blueprint_json,
            tech_stack_json=original.tech_stack_json,
            architecture_json=original.architecture_json,
            requirements_json=original.requirements_json,
            database_schema_json=original.database_schema_json,
            api_contracts_json=original.api_contracts_json,
            folder_tree_json=original.folder_tree_json,
            roadmap_json=original.roadmap_json,
        )
        return await self.repo.create_blueprint(db, cloned)

    async def export_blueprint(
        self, db: AsyncSession, owner_id: UUID, req: ExportRequest
    ) -> Dict[str, str]:
        blueprint = await self.get_blueprint(db, owner_id, req.blueprint_id)
        return self.engine.export_blueprint_document(blueprint.blueprint_json, req.format)

    async def get_metrics(self, db: AsyncSession, owner_id: UUID) -> ProjectMetricsResponse:
        blueprints, total = await self.repo.list_blueprints(db, owner_id, page=1, page_size=100)
        
        breakdown: Dict[str, int] = {}
        tech_counts: Dict[str, int] = {}
        total_versions = 0

        for bp in blueprints:
            b_type = bp.project_type or "web_app"
            breakdown[b_type] = breakdown.get(b_type, 0) + 1
            total_versions += len(bp.versions)

            primary = bp.tech_stack_json.get("recommended_primary", {})
            for cat, tech in primary.items():
                if tech:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1

        top_techs = [{"technology": k, "count": v} for k, v in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

        return ProjectMetricsResponse(
            total_blueprints=total,
            project_types_breakdown=breakdown,
            most_recommended_technologies=top_techs,
            total_versions_snapshot=total_versions,
        )

    def get_starter_templates(self) -> List[ProjectTemplateResponse]:
        templates = self.engine.get_starter_templates()
        return [ProjectTemplateResponse(**t) for t in templates]


project_generator_service = ProjectGeneratorService()
