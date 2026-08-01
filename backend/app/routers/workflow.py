from typing import List
from fastapi import APIRouter, Depends, status
from app.models.user import User
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.services.workflow_service import workflow_service
from app.routers.deps import get_current_active_user

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(current_user: User = Depends(get_current_active_user)):
    """List registered automation workflows for current user."""
    return await workflow_service.list_workflows(user_id=current_user.id)


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    item: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new automation workflow pipeline."""
    return await workflow_service.create_workflow(user_id=current_user.id, item=item)
