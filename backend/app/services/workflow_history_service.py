from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import WorkflowExecution
from app.repositories.workflow_repository import workflow_repository


class WorkflowHistoryService:
    """Service handling workflow execution history, node logs, and trace audits."""

    def __init__(self):
        self.repo = workflow_repository

    async def get_execution_history(
        self, db: AsyncSession, owner_id: UUID, workflow_id: Optional[UUID] = None, limit: int = 20
    ) -> List[WorkflowExecution]:
        return await self.repo.list_executions(db, user_id=owner_id, workflow_id=workflow_id, limit=limit)

    async def get_execution_details(
        self, db: AsyncSession, owner_id: UUID, execution_id: UUID
    ) -> Optional[WorkflowExecution]:
        return await self.repo.get_execution(db, user_id=owner_id, execution_id=execution_id)


workflow_history_service = WorkflowHistoryService()
