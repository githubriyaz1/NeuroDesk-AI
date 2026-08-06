from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation reference for source attribution in LLM responses."""
    asset_id: UUID
    asset_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    source_type: str  # pdf, csv, excel, metadata, image_metadata, plain_text, search
    snippet: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_badge(self) -> str:
        page_str = f", Page {self.page_number}" if self.page_number else ""
        return f"[Source: {self.asset_name}{page_str}]"


class RetrievedDocument(BaseModel):
    """Individual document chunk or record retrieved by a BaseRetriever."""
    id: str
    asset_id: UUID
    asset_name: str
    content: str
    source_type: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    score: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    def to_citation(self) -> Citation:
        return Citation(
            asset_id=self.asset_id,
            asset_name=self.asset_name,
            page_number=self.page_number,
            section=self.section,
            confidence_score=round(self.score, 4),
            source_type=self.source_type,
            snippet=self.content[:250] + ("..." if len(self.content) > 250 else ""),
            metadata=self.metadata,
        )


class KnowledgeQueryRequest(BaseModel):
    """Request payload for knowledge engine retrieval."""
    query: str
    conversation_id: Optional[UUID] = None
    asset_ids: Optional[List[UUID]] = None
    limit: int = Field(default=5, ge=1, le=20)
    min_confidence: float = Field(default=0.1, ge=0.0, le=1.0)
    retriever_types: Optional[List[str]] = None


class KnowledgeQueryResult(BaseModel):
    """Result returned by KnowledgeEngine retrieval pipeline."""
    query: str
    documents: List[RetrievedDocument]
    citations: List[Citation]
    packaged_context: str
    total_found: int
    retrieval_latency_ms: float
    retrievers_used: List[str]


class KnowledgeIndexItem(BaseModel):
    """Indexed document representation in the Knowledge Index."""
    asset_id: UUID
    asset_name: str
    file_type: str
    indexed_text: str
    metadata_fields: Dict[str, Any]
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeDiagnosticsResponse(BaseModel):
    """Knowledge engine health, statistics, and cache metrics."""
    status: str = "healthy"
    knowledge_index_health: str = "operational"
    retriever_health: Dict[str, str] = Field(default_factory=dict)
    indexed_assets_count: int = 0
    indexed_chunks_count: int = 0
    average_retrieval_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    active_retrievers: List[str] = Field(default_factory=list)
