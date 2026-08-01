from typing import List
from fastapi import APIRouter, Depends, status
from app.models.user import User
from app.schemas.ai_studio import AIModelCreate, AIModelResponse
from app.services.ai_studio_service import ai_studio_service
from app.routers.deps import get_current_active_user

router = APIRouter(prefix="/ai-studio", tags=["AI Studio"])


@router.get("/models", response_model=List[AIModelResponse])
async def list_models(current_user: User = Depends(get_current_active_user)):
    """List registered AI Studio machine learning models for current user."""
    return await ai_studio_service.list_models(user_id=current_user.id)


@router.post("/models", response_model=AIModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_in: AIModelCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Register and configure a new model in AI Studio."""
    return await ai_studio_service.create_model(user_id=current_user.id, model_in=model_in)
