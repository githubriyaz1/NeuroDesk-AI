from typing import List
from fastapi import APIRouter, Depends, status
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.services.workspace_service import workspace_service
from app.routers.deps import get_current_active_user

router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspace_items(current_user: User = Depends(get_current_active_user)):
    """List datasets and documents in the workspace for current user."""
    return await workspace_service.list_workspaces(user_id=current_user.id)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace_item(
    item: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
):
    """Add a new dataset or document to the workspace."""
    return await workspace_service.create_workspace(user_id=current_user.id, item=item)
