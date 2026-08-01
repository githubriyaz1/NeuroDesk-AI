from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from app.schemas.workflow import WorkflowCreate, WorkflowResponse


class WorkflowService:
    """Service handling automated workflow execution pipelines."""

    async def list_workflows(self, user_id: UUID) -> List[WorkflowResponse]:
        """Return sample registered workflows."""
        now = datetime.utcnow()
        return [
            WorkflowResponse(
                id=UUID("55555555-5555-5555-5555-555555555555"),
                name="Automated Nightly Dataset Ingestion & Validation",
                description="Fetches raw telemetry data from S3, executes data quality checks, and triggers AI Studio retraining.",
                owner_id=user_id,
                definition={
                    "triggers": [{"type": "cron", "schedule": "0 2 * * *"}],
                    "steps": [
                        {"step": 1, "action": "ingest_s3", "target": "bucket/telemetry"},
                        {"step": 2, "action": "data_quality_check", "rules": ["no_null_keys"]},
                        {"step": 3, "action": "trigger_model_eval", "model_id": "33333333-3333-3333-3333-333333333333"},
                    ],
                },
                is_enabled=True,
                created_at=now,
                updated_at=now,
            ),
        ]

    async def create_workflow(self, user_id: UUID, item: WorkflowCreate) -> WorkflowResponse:
        """Create new automation workflow."""
        now = datetime.utcnow()
        return WorkflowResponse(
            id=uuid4(),
            name=item.name,
            description=item.description,
            owner_id=user_id,
            definition=item.definition,
            is_enabled=item.is_enabled if item.is_enabled is not None else True,
            created_at=now,
            updated_at=now,
        )


workflow_service = WorkflowService()
