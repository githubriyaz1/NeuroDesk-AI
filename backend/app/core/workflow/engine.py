from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.workflow.compiler import workflow_compiler
from app.core.workflow.executor import workflow_executor
from app.core.workflow.validator import workflow_validator
from app.models.workflow import WorkflowExecution


class WorkflowEngine:
    """Primary facade for Enterprise AI Workflow Automation Studio."""

    def __init__(self):
        self.validator = workflow_validator
        self.compiler = workflow_compiler
        self.executor = workflow_executor

    def validate_workflow(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        return self.validator.validate_graph(nodes, edges)

    async def execute_workflow(
        self,
        db: AsyncSession,
        execution: WorkflowExecution,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        variables: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        return await self.executor.execute(db, execution, nodes, edges, initial_variables=variables)


workflow_engine = WorkflowEngine()
