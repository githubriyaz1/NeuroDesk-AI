import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.workflow.compiler import workflow_compiler
from app.core.workflow.runner import workflow_runner
from app.core.workflow.validator import workflow_validator
from app.models.workflow import ExecutionLog, ExecutionStatus, WorkflowExecution, WorkflowExecutionNode
from app.repositories.workflow_repository import workflow_repository


class WorkflowExecutor:
    """DAG engine that executes workflow execution plans in topological order with context passing."""

    def __init__(self):
        self.validator = workflow_validator
        self.compiler = workflow_compiler
        self.runner = workflow_runner
        self.repo = workflow_repository

    async def execute(
        self,
        db: AsyncSession,
        execution: WorkflowExecution,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        initial_variables: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        start_time = time.time()
        execution.status = ExecutionStatus.RUNNING.value
        await db.flush()

        try:
            # Validate DAG graph
            is_valid, errors = self.validator.validate_graph(nodes, edges)
            if not is_valid:
                raise ValueError(f"Invalid workflow graph structure: {'; '.join(errors)}")

            comp_log = ExecutionLog(
                execution_id=execution.id,
                log_level="INFO",
                message="Workflow DAG compilation completed successfully.",
            )
            await self.repo.add_log(db, comp_log)
            execution.logs.append(comp_log)

            # Compile topological execution order
            plan = self.compiler.compile_plan(nodes, edges)

            context: Dict[str, Any] = {
                "inputs": execution.inputs_json or {},
                "variables": initial_variables or {},
                "last_output": None,
            }

            for node in plan:
                node_id = node["id"]
                node_type = node.get("type", "unknown")

                node_rec = WorkflowExecutionNode(
                    execution_id=execution.id,
                    node_id=node_id,
                    node_type=node_type,
                    status=ExecutionStatus.RUNNING.value,
                    inputs_json={"context": context.get("last_output")},
                    started_at=datetime.now(timezone.utc),
                )
                await self.repo.add_execution_node(db, node_rec)
                execution.nodes.append(node_rec)

                exec_log = ExecutionLog(
                    execution_id=execution.id,
                    node_id=node_id,
                    log_level="INFO",
                    message=f"Executing node '{node.get('label', node_id)}' ({node_type})",
                )
                await self.repo.add_log(db, exec_log)
                execution.logs.append(exec_log)

                try:
                    outputs = await self.runner.run_node(
                        node=node,
                        context=context,
                        db_session=db,
                        owner_id=execution.owner_id,
                    )
                    context["last_output"] = outputs
                    node_rec.status = ExecutionStatus.SUCCESS.value
                    node_rec.outputs_json = outputs
                    node_rec.latency_ms = outputs.get("latency_ms", 0.0)
                    node_rec.completed_at = datetime.now(timezone.utc)

                except Exception as node_err:
                    node_rec.status = ExecutionStatus.FAILED.value
                    node_rec.error_message = str(node_err)
                    node_rec.completed_at = datetime.now(timezone.utc)
                    err_log = ExecutionLog(
                        execution_id=execution.id,
                        node_id=node_id,
                        log_level="ERROR",
                        message=f"Node '{node_id}' failed: {str(node_err)}",
                    )
                    await self.repo.add_log(db, err_log)
                    execution.logs.append(err_log)
                    raise node_err

            execution.status = ExecutionStatus.SUCCESS.value
            execution.outputs_json = context.get("last_output") or {}
            execution.execution_context_json = context.get("variables") or {}

        except Exception as err:
            execution.status = ExecutionStatus.FAILED.value
            execution.error_message = str(err)
            fail_log = ExecutionLog(
                execution_id=execution.id,
                log_level="ERROR",
                message=f"Workflow execution failed: {str(err)}",
            )
            await self.repo.add_log(db, fail_log)
            execution.logs.append(fail_log)

        finally:
            execution.total_latency_ms = round((time.time() - start_time) * 1000.0, 2)
            execution.completed_at = datetime.now(timezone.utc)
            await db.flush()

        return execution


workflow_executor = WorkflowExecutor()
