from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.workflow import ExecutionLog, Workflow, WorkflowExecution, WorkflowExecutionNode, WorkflowVersion


class WorkflowRepository:
    """Repository for managing workflows, versions, executions, nodes, and logs."""

    async def create_workflow(self, db: AsyncSession, workflow: Workflow) -> Workflow:
        db.add(workflow)
        await db.flush()
        await db.refresh(workflow)
        return workflow

    async def get_workflow_by_id(
        self, db: AsyncSession, user_id: UUID, workflow_id: UUID
    ) -> Optional[Workflow]:
        stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.owner_id == user_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_workflows(
        self,
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        is_template: Optional[bool] = None,
    ) -> Tuple[List[Workflow], int]:
        stmt = select(Workflow).where(Workflow.owner_id == user_id)
        if status:
            stmt = stmt.where(Workflow.status == status)
        if is_template is not None:
            stmt = stmt.where(Workflow.is_template == is_template)

        stmt = stmt.order_by(Workflow.updated_at.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def save_workflow(self, db: AsyncSession, workflow: Workflow) -> Workflow:
        db.add(workflow)
        await db.flush()
        await db.refresh(workflow)
        return workflow

    async def create_version(self, db: AsyncSession, version: WorkflowVersion) -> WorkflowVersion:
        db.add(version)
        await db.flush()
        return version

    async def create_execution(self, db: AsyncSession, execution: WorkflowExecution) -> WorkflowExecution:
        db.add(execution)
        await db.flush()
        await db.refresh(execution)
        return execution

    async def get_execution(
        self, db: AsyncSession, user_id: UUID, execution_id: UUID
    ) -> Optional[WorkflowExecution]:
        stmt = (
            select(WorkflowExecution)
            .options(selectinload(WorkflowExecution.nodes), selectinload(WorkflowExecution.logs))
            .where(WorkflowExecution.id == execution_id, WorkflowExecution.owner_id == user_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_executions(
        self, db: AsyncSession, user_id: UUID, workflow_id: Optional[UUID] = None, limit: int = 20
    ) -> List[WorkflowExecution]:
        stmt = (
            select(WorkflowExecution)
            .options(selectinload(WorkflowExecution.nodes), selectinload(WorkflowExecution.logs))
            .where(WorkflowExecution.owner_id == user_id)
        )
        if workflow_id:
            stmt = stmt.where(WorkflowExecution.workflow_id == workflow_id)
        stmt = stmt.order_by(WorkflowExecution.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def add_execution_node(
        self, db: AsyncSession, node: WorkflowExecutionNode
    ) -> WorkflowExecutionNode:
        db.add(node)
        await db.flush()
        return node

    async def add_log(self, db: AsyncSession, log: ExecutionLog) -> ExecutionLog:
        db.add(log)
        await db.flush()
        return log


workflow_repository = WorkflowRepository()
