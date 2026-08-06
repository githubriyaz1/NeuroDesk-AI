from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.workflow import workflow_engine
from app.models.workflow import ExecutionStatus, Workflow, WorkflowExecution, WorkflowStatus, WorkflowVersion
from app.repositories.workflow_repository import workflow_repository
from app.schemas.workflow import WorkflowCreate, WorkflowRunRequest, WorkflowUpdate


class WorkflowService:
    """Primary domain service for Workflow Studio management, execution, and version control."""

    def __init__(self):
        self.repo = workflow_repository
        self.engine = workflow_engine

    async def create_workflow(self, db: AsyncSession, owner_id: UUID, payload: WorkflowCreate) -> Workflow:
        nodes_dict = [n.model_dump() for n in payload.nodes]
        edges_dict = [e.model_dump() for e in payload.edges]

        # Auto-populate default starter nodes if empty
        if not nodes_dict:
            nodes_dict = [
                {"id": "start_1", "type": "start", "label": "Start Entry", "position": {"x": 100, "y": 150}, "data": {}},
                {"id": "llm_1", "type": "llm_prompt", "label": "LLM Prompt", "position": {"x": 450, "y": 150}, "data": {"prompt": "Analyze input: {input}"}},
                {"id": "end_1", "type": "end", "label": "End Output", "position": {"x": 800, "y": 150}, "data": {}},
            ]
            edges_dict = [
                {"id": "e_1", "source": "start_1", "target": "llm_1"},
                {"id": "e_2", "source": "llm_1", "target": "end_1"},
            ]

        # Validate graph topology
        is_valid, errors = self.engine.validate_workflow(nodes_dict, edges_dict)
        if not is_valid:
            raise ValueError(f"Invalid workflow graph: {'; '.join(errors)}")

        wf = Workflow(
            owner_id=owner_id,
            name=payload.name,
            description=payload.description,
            is_template=payload.is_template,
            tags=payload.tags,
            nodes_json=nodes_dict,
            edges_json=edges_dict,
            variables_json=payload.variables,
            status=WorkflowStatus.ACTIVE.value,
        )
        wf = await self.repo.create_workflow(db, wf)

        # Create version 1 snapshot
        version_snap = WorkflowVersion(
            workflow_id=wf.id,
            version_number=1,
            nodes_json=nodes_dict,
            edges_json=edges_dict,
            variables_json=payload.variables,
            changelog="Initial workflow creation",
        )
        await self.repo.create_version(db, version_snap)

        return wf

    async def get_workflow(self, db: AsyncSession, owner_id: UUID, workflow_id: UUID) -> Workflow:
        wf = await self.repo.get_workflow_by_id(db, user_id=owner_id, workflow_id=workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found or access denied.")
        return wf

    async def list_workflows(
        self, db: AsyncSession, owner_id: UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Workflow], int]:
        return await self.repo.list_workflows(db, user_id=owner_id, page=page, page_size=page_size)

    async def update_workflow(
        self, db: AsyncSession, owner_id: UUID, workflow_id: UUID, payload: WorkflowUpdate
    ) -> Workflow:
        wf = await self.get_workflow(db, owner_id, workflow_id)

        if payload.nodes is not None:
            wf.nodes_json = [n.model_dump() for n in payload.nodes]
        if payload.edges is not None:
            wf.edges_json = [e.model_dump() for e in payload.edges]

        if payload.nodes is not None or payload.edges is not None:
            is_valid, errors = self.engine.validate_workflow(wf.nodes_json, wf.edges_json)
            if not is_valid:
                raise ValueError(f"Updated workflow graph is invalid: {'; '.join(errors)}")

        if payload.name is not None:
            wf.name = payload.name
        if payload.description is not None:
            wf.description = payload.description
        if payload.status is not None:
            wf.status = payload.status
        if payload.tags is not None:
            wf.tags = payload.tags
        if payload.variables is not None:
            wf.variables_json = payload.variables

        wf.version += 1
        wf = await self.repo.save_workflow(db, wf)

        # Snapshot version
        version_snap = WorkflowVersion(
            workflow_id=wf.id,
            version_number=wf.version,
            nodes_json=wf.nodes_json,
            edges_json=wf.edges_json,
            variables_json=wf.variables_json,
            changelog=f"Updated to version {wf.version}",
        )
        await self.repo.create_version(db, version_snap)

        return wf

    async def run_workflow(
        self, db: AsyncSession, owner_id: UUID, workflow_id: UUID, payload: WorkflowRunRequest
    ) -> WorkflowExecution:
        wf = await self.get_workflow(db, owner_id, workflow_id)

        execution = WorkflowExecution(
            workflow_id=wf.id,
            owner_id=owner_id,
            status=ExecutionStatus.PENDING.value,
            trigger_source=payload.trigger_source,
            inputs_json=payload.inputs,
            execution_context_json=wf.variables_json or {},
        )
        execution = await self.repo.create_execution(db, execution)

        # Execute workflow runner synchronously in DB context
        return await self.engine.execute_workflow(
            db=db,
            execution=execution,
            nodes=wf.nodes_json,
            edges=wf.edges_json,
            variables=wf.variables_json,
        )

    async def cancel_execution(self, db: AsyncSession, owner_id: UUID, execution_id: UUID) -> WorkflowExecution:
        execution = await self.repo.get_execution(db, user_id=owner_id, execution_id=execution_id)
        if not execution:
            raise ValueError(f"Execution '{execution_id}' not found.")

        execution.status = ExecutionStatus.CANCELLED.value
        return await self.repo.create_execution(db, execution)

    async def duplicate_workflow(self, db: AsyncSession, owner_id: UUID, workflow_id: UUID) -> Workflow:
        wf = await self.get_workflow(db, owner_id, workflow_id)
        dup_payload = WorkflowCreate(
            name=f"{wf.name} (Copy)",
            description=wf.description,
            is_template=False,
            tags=wf.tags or [],
            nodes=wf.nodes_json or [],
            edges=wf.edges_json or [],
            variables=wf.variables_json or {},
        )
        return await self.create_workflow(db, owner_id, dup_payload)


workflow_service = WorkflowService()
