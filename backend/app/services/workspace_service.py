from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate


class WorkspaceService:
    """Service handling Workspace dataset and document lifecycle operations."""

    async def list_workspaces(self, user_id: UUID) -> List[WorkspaceResponse]:
        """Return sample workspace datasets and documents for initial workspace setup."""
        now = datetime.now(timezone.utc)
        return [
            WorkspaceResponse(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                name="Customer Churn Dataset 2026",
                description="E-commerce customer behavior dataset for churn prediction analysis.",
                owner_id=user_id,
                file_path="/storage/datasets/customer_churn_v2.csv",
                file_type="csv",
                file_size_bytes=14589200,
                status="ready",
                meta_data={"rows": 125000, "columns": 34, "format": "Structured CSV"},
                created_at=now,
                updated_at=now,
            ),
            WorkspaceResponse(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                name="Financial Q2 Performance Report",
                description="Enterprise quarterly revenue forecast and expense documents.",
                owner_id=user_id,
                file_path="/storage/documents/q2_finance_report.pdf",
                file_type="pdf",
                file_size_bytes=4820100,
                status="ready",
                meta_data={"pages": 48, "vectorized": True, "embedding_model": "text-embedding-3"},
                created_at=now,
                updated_at=now,
            ),
        ]

    async def create_workspace(self, user_id: UUID, item: WorkspaceCreate) -> WorkspaceResponse:
        """Create new workspace entry placeholder."""
        now = datetime.now(timezone.utc)
        return WorkspaceResponse(
            id=uuid4(),
            name=item.name,
            description=item.description,
            owner_id=user_id,
            file_path=None,
            file_type=item.file_type or "dataset",
            file_size_bytes=0,
            status="created",
            meta_data=item.meta_data or {},
            created_at=now,
            updated_at=now,
        )


workspace_service = WorkspaceService()
