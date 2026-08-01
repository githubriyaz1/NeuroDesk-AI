from typing import List
from fastapi import APIRouter, Depends, status
from app.models.user import User
from app.schemas.project_generator import ProjectGenerateRequest, ProjectBlueprintResponse
from app.services.project_generator_service import project_generator_service
from app.routers.deps import get_current_active_user

router = APIRouter(prefix="/project-generator", tags=["AI Project Generator"])


@router.post("/generate", response_model=ProjectBlueprintResponse, status_code=status.HTTP_201_CREATED)
async def generate_blueprint(
    req: ProjectGenerateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Generates a structured software architecture blueprint."""
    return await project_generator_service.generate_blueprint(user_id=current_user.id, req=req)


@router.get("/blueprints", response_model=List[ProjectBlueprintResponse])
async def list_blueprints(current_user: User = Depends(get_current_active_user)):
    """Lists saved project architecture blueprints."""
    return await project_generator_service.list_blueprints(user_id=current_user.id)
