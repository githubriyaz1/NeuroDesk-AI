from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project_generator import BlueprintVersion, ProjectBlueprint


class ProjectGeneratorRepository:
    """Async repository for managing project blueprints and version history."""

    async def create_blueprint(self, db: AsyncSession, blueprint: ProjectBlueprint) -> ProjectBlueprint:
        db.add(blueprint)
        await db.flush()
        await db.refresh(blueprint)
        # Fetch with eager loaded versions
        return await self.get_blueprint_by_id(db, blueprint.owner_id, blueprint.id) or blueprint

    async def get_blueprint_by_id(
        self, db: AsyncSession, user_id: UUID, blueprint_id: UUID
    ) -> Optional[ProjectBlueprint]:
        stmt = (
            select(ProjectBlueprint)
            .options(selectinload(ProjectBlueprint.versions))
            .where(ProjectBlueprint.id == blueprint_id, ProjectBlueprint.owner_id == user_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_blueprints(
        self,
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        project_type: Optional[str] = None,
        is_template: Optional[bool] = None,
    ) -> Tuple[List[ProjectBlueprint], int]:
        stmt = select(ProjectBlueprint).options(selectinload(ProjectBlueprint.versions)).where(ProjectBlueprint.owner_id == user_id)
        if project_type:
            stmt = stmt.where(ProjectBlueprint.project_type == project_type)
        if is_template is not None:
            stmt = stmt.where(ProjectBlueprint.is_template == is_template)

        stmt = stmt.order_by(ProjectBlueprint.updated_at.desc())

        count_stmt = select(func.count()).select_from(select(ProjectBlueprint.id).where(ProjectBlueprint.owner_id == user_id).subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def save_blueprint(self, db: AsyncSession, blueprint: ProjectBlueprint) -> ProjectBlueprint:
        db.add(blueprint)
        await db.flush()
        return await self.get_blueprint_by_id(db, blueprint.owner_id, blueprint.id) or blueprint

    async def create_version(self, db: AsyncSession, version: BlueprintVersion) -> BlueprintVersion:
        db.add(version)
        await db.flush()
        return version

    async def list_versions(self, db: AsyncSession, blueprint_id: UUID) -> List[BlueprintVersion]:
        stmt = (
            select(BlueprintVersion)
            .where(BlueprintVersion.blueprint_id == blueprint_id)
            .order_by(BlueprintVersion.version_number.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def delete_blueprint(self, db: AsyncSession, user_id: UUID, blueprint_id: UUID) -> bool:
        blueprint = await self.get_blueprint_by_id(db, user_id, blueprint_id)
        if blueprint:
            await db.delete(blueprint)
            await db.flush()
            return True
        return False


project_generator_repository = ProjectGeneratorRepository()
