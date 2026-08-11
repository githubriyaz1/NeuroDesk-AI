import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.workflow.compiler import workflow_compiler
from app.core.workflow.runner import workflow_runner
from app.core.workflow.validator import workflow_validator
from app.models.workflow import ExecutionLog, ExecutionStatus, WorkflowExecution, WorkflowExecutionNode
from app.repositories.workflow_repository import workflow_repository


class WorkflowExecutor:
    """DAG engine that executes workflow execution plans in topological order with context passing, retries, and conditional branch skipping."""

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
                "node_outputs": {},
            }

            skipped_nodes: Set[str] = set()

            # Pre-build adjacency for edge handle routing
            edge_map: Dict[str, List[Dict[str, Any]]] = {}
            for e in edges:
                src = e["source"]
                if src not in edge_map:
                    edge_map[src] = []
                edge_map[src].append(e)

            for node in plan:
                node_id = node["id"]
                node_type = node.get("type", "unknown")

                # Check if execution was cancelled in DB or externally
                if execution.status == ExecutionStatus.CANCELLED.value:
                    cancel_log = ExecutionLog(
                        execution_id=execution.id,
                        node_id=node_id,
                        log_level="WARNING",
                        message=f"Execution cancelled prior to running node '{node_id}'. Marking node CANCELLED.",
                    )
                    await self.repo.add_log(db, cancel_log)
                    execution.logs.append(cancel_log)

                    node_rec = WorkflowExecutionNode(
                        execution_id=execution.id,
                        node_id=node_id,
                        node_type=node_type,
                        status=ExecutionStatus.CANCELLED.value,
                        inputs_json={},
                        completed_at=datetime.now(timezone.utc),
                    )
                    await self.repo.add_execution_node(db, node_rec)
                    execution.nodes.append(node_rec)
                    continue

                # Check if this node was skipped due to conditional branch evaluation
                if node_id in skipped_nodes:
                    skip_log = ExecutionLog(
                        execution_id=execution.id,
                        node_id=node_id,
                        log_level="INFO",
                        message=f"Node '{node.get('label', node_id)}' ({node_type}) was SKIPPED due to conditional branch evaluation.",
                    )
                    await self.repo.add_log(db, skip_log)
                    execution.logs.append(skip_log)

                    node_rec = WorkflowExecutionNode(
                        execution_id=execution.id,
                        node_id=node_id,
                        node_type=node_type,
                        status=ExecutionStatus.SKIPPED.value,
                        inputs_json={"reason": "Conditional branch inactive"},
                        completed_at=datetime.now(timezone.utc),
                    )
                    await self.repo.add_execution_node(db, node_rec)
                    execution.nodes.append(node_rec)

                    # Propagate skip state to all downstream target nodes
                    for out_edge in edge_map.get(node_id, []):
                        skipped_nodes.add(out_edge["target"])
                    continue

                # Prepare execution record for running node
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

                # Retry Policy Configuration
                data = node.get("data", {})
                max_retries = int(data.get("max_retries", 0))
                backoff_seconds = float(data.get("backoff_seconds", 1.0))
                attempt = 0
                node_success = False
                last_error = None
                outputs = {}

                while attempt <= max_retries:
                    attempt += 1
                    if attempt > 1:
                        retry_log = ExecutionLog(
                            execution_id=execution.id,
                            node_id=node_id,
                            log_level="WARNING",
                            message=f"Node '{node_id}' retry Attempt {attempt} of {max_retries + 1} after backoff {backoff_seconds}s...",
                        )
                        await self.repo.add_log(db, retry_log)
                        execution.logs.append(retry_log)
                        await asyncio.sleep(backoff_seconds)

                    try:
                        outputs = await self.runner.run_node(
                            node=node,
                            context=context,
                            db_session=db,
                            owner_id=execution.owner_id,
                        )
                        node_success = True
                        break
                    except (ValueError, TimeoutError) as sec_err:
                        # Non-retryable security / validation / timeout error
                        last_error = sec_err
                        break
                    except Exception as err:
                        last_error = err

                node_rec.retry_count = attempt - 1

                if node_success:
                    context["last_output"] = outputs
                    context["node_outputs"][node_id] = outputs
                    node_rec.status = ExecutionStatus.SUCCESS.value
                    node_rec.outputs_json = outputs
                    node_rec.latency_ms = outputs.get("latency_ms", 0.0)
                    node_rec.completed_at = datetime.now(timezone.utc)

                    # Handle Conditional Branch Activation
                    if node_type == "conditional":
                        active_branch = str(outputs.get("branch", "true")).lower()
                        # Find out-edges from this conditional node
                        conditional_edges = edge_map.get(node_id, [])
                        for ce in conditional_edges:
                            handle = str(ce.get("source_handle") or ce.get("condition_expr") or "").lower()
                            if handle and handle != active_branch:
                                # Deactive unselected branch target
                                skipped_nodes.add(ce["target"])

                else:
                    node_rec.status = ExecutionStatus.FAILED.value
                    node_rec.error_message = str(last_error)
                    node_rec.completed_at = datetime.now(timezone.utc)
                    err_log = ExecutionLog(
                        execution_id=execution.id,
                        node_id=node_id,
                        log_level="ERROR",
                        message=f"Node '{node_id}' failed after {attempt} attempt(s): {str(last_error)}",
                    )
                    await self.repo.add_log(db, err_log)
                    execution.logs.append(err_log)
                    raise last_error

            if execution.status != ExecutionStatus.CANCELLED.value:
                execution.status = ExecutionStatus.SUCCESS.value
                execution.outputs_json = context.get("last_output") or {}
                execution.execution_context_json = context.get("variables") or {}

        except Exception as err:
            if execution.status != ExecutionStatus.CANCELLED.value:
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
