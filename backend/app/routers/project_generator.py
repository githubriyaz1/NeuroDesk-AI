from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.project_generator import (
    BlueprintUpdateRequest,
    ExportRequest,
    ProjectBlueprintResponse,
    ProjectGenerationRequest,
    ProjectMetricsResponse,
    ProjectTemplateResponse,
)
from app.services.project_generator_service import project_generator_service

router = APIRouter(prefix="/ai-studio", tags=["AI Studio & Intelligent Project Generator"])


@router.post("/generate", response_model=ProjectBlueprintResponse, status_code=status.HTTP_201_CREATED)
async def generate_project_blueprint(
    payload: ProjectGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generates a complete software project blueprint from a plain English prompt."""
    try:
        return await project_generator_service.generate_blueprint(db, current_user.id, payload)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/blueprints/templates/starter", response_model=List[ProjectTemplateResponse], status_code=status.HTTP_200_OK)
async def get_starter_templates():
    """Returns pre-configured starter project blueprint templates."""
    return project_generator_service.get_starter_templates()


@router.get("/blueprints/metrics", response_model=ProjectMetricsResponse, status_code=status.HTTP_200_OK)
async def get_ai_studio_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns analytics metrics for AI Studio project blueprints."""
    return await project_generator_service.get_metrics(db, current_user.id)


@router.get("/blueprints", response_model=List[ProjectBlueprintResponse], status_code=status.HTTP_200_OK)
async def list_blueprints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists saved project blueprints for the current user."""
    return await project_generator_service.list_blueprints(db, current_user.id, page, page_size, project_type)


@router.get("/blueprints/{blueprint_id}", response_model=ProjectBlueprintResponse, status_code=status.HTTP_200_OK)
async def get_blueprint(
    blueprint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full details of a specific project blueprint."""
    try:
        return await project_generator_service.get_blueprint(db, current_user.id, blueprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/blueprints/{blueprint_id}", response_model=ProjectBlueprintResponse, status_code=status.HTTP_200_OK)
async def update_blueprint(
    blueprint_id: UUID,
    payload: BlueprintUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates blueprint requirements, architecture, tech stack, or database schema."""
    try:
        return await project_generator_service.update_blueprint(db, current_user.id, blueprint_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/blueprints/{blueprint_id}/clone", response_model=ProjectBlueprintResponse, status_code=status.HTTP_201_CREATED)
async def clone_blueprint(
    blueprint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clones an existing blueprint."""
    try:
        return await project_generator_service.clone_blueprint(db, current_user.id, blueprint_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/export", status_code=status.HTTP_200_OK)
async def export_blueprint(
    payload: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exports blueprint into Markdown, JSON, YAML, or PDF format."""
    try:
        return await project_generator_service.export_blueprint(db, current_user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
