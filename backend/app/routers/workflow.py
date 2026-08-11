from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowExecutionResponse,
    WorkflowResponse,
    WorkflowRunRequest,
    WorkflowTemplateResponse,
    WorkflowUpdate,
)
from app.services.workflow_history_service import workflow_history_service
from app.services.workflow_metrics_service import workflow_metrics_service
from app.services.workflow_service import workflow_service
from app.services.workflow_template_service import workflow_template_service

router = APIRouter(prefix="/workflows", tags=["Enterprise AI Workflow Automation Studio"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new workflow graph with validation and initial version snapshot."""
    try:
        return await workflow_service.create_workflow(db, current_user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create workflow: {str(e)}")


@router.get("", response_model=List[WorkflowResponse], status_code=status.HTTP_200_OK)
async def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists user workflows with pagination."""
    workflows, _ = await workflow_service.list_workflows(db, current_user.id, page=page, page_size=page_size)
    return workflows


@router.get("/templates", response_model=List[WorkflowTemplateResponse], status_code=status.HTTP_200_OK)
async def get_templates(
    current_user: User = Depends(get_current_user),
):
    """Returns pre-built starter workflow templates."""
    return workflow_template_service.get_starter_templates()


@router.get("/metrics", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_workflow_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns execution metrics and latency statistics across user workflows."""
    return await workflow_metrics_service.get_user_workflow_metrics(db, current_user.id)


@router.get("/executions", response_model=List[WorkflowExecutionResponse], status_code=status.HTTP_200_OK)
async def list_executions(
    workflow_id: Optional[UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists execution history for user workflows."""
    return await workflow_history_service.get_execution_history(db, current_user.id, workflow_id=workflow_id, limit=limit)


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse, status_code=status.HTTP_200_OK)
async def get_execution_details(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns full execution trace, node statuses, and execution logs."""
    exec_rec = await workflow_history_service.get_execution_details(db, current_user.id, execution_id)
    if not exec_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found.")
    return exec_rec


@router.get("/{workflow_id}", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)
async def get_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves workflow details by ID."""
    try:
        return await workflow_service.get_workflow(db, current_user.id, workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{workflow_id}", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)
async def update_workflow(
    workflow_id: UUID,
    payload: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates workflow nodes, edges, or metadata and creates a new version snapshot."""
    try:
        return await workflow_service.update_workflow(db, current_user.id, workflow_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{workflow_id}/run", response_model=WorkflowExecutionResponse, status_code=status.HTTP_200_OK)
async def run_workflow(
    workflow_id: UUID,
    payload: WorkflowRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executes a workflow graph in topological dependency order."""
    try:
        return await workflow_service.run_workflow(db, current_user.id, workflow_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Duplicates an existing workflow graph."""
    try:
        return await workflow_service.duplicate_workflow(db, current_user.id, workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a workflow and all associated version and execution records."""
    try:
        await workflow_service.delete_workflow(db, current_user.id, workflow_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{workflow_id}/export", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def export_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exports workflow DAG specification as clean JSON."""
    try:
        return await workflow_service.export_workflow(db, current_user.id, workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/import", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def import_workflow(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Imports workflow DAG specification from JSON."""
    try:
        return await workflow_service.import_workflow(db, current_user.id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/executions/{execution_id}/cancel", response_model=WorkflowExecutionResponse, status_code=status.HTTP_200_OK)
async def cancel_execution(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancels a running workflow execution."""
    try:
        return await workflow_service.cancel_execution(db, current_user.id, execution_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
