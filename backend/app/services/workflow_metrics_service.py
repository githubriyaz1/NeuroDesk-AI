from typing import Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.workflow_repository import workflow_repository


class WorkflowMetricsService:
    """Calculates execution metrics, success rates, and average latencies across workflow runs."""

    def __init__(self):
        self.repo = workflow_repository

    async def get_user_workflow_metrics(self, db: AsyncSession, owner_id: UUID) -> Dict[str, Any]:
        executions = await self.repo.list_executions(db, user_id=owner_id, limit=100)
        total_runs = len(executions)
        successful_runs = len([e for e in executions if e.status == "SUCCESS"])
        failed_runs = len([e for e in executions if e.status == "FAILED"])
        cancelled_runs = len([e for e in executions if e.status == "CANCELLED"])

        latencies = [e.total_latency_ms for e in executions if e.total_latency_ms > 0]
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        return {
            "total_executions": total_runs,
            "successful_executions": successful_runs,
            "failed_executions": failed_runs,
            "cancelled_executions": cancelled_runs,
            "success_rate_percentage": round((successful_runs / total_runs * 100) if total_runs > 0 else 100.0, 2),
            "average_latency_ms": avg_latency,
        }


workflow_metrics_service = WorkflowMetricsService()
