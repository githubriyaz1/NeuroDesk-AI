from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class InsightItem(BaseModel):
    """Individual AI insight record."""
    category: str  # executive_summary, key_finding, recommendation, risk, opportunity, next_step
    title: str
    description: str
    impact_level: str = "medium"  # high, medium, low
    confidence_score: float = 0.85


class DocumentAnalysisResponse(BaseModel):
    """Comprehensive analysis report for document assets (PDF, TXT, Markdown)."""
    asset_id: UUID
    filename: str
    mime_type: str
    executive_summary: str
    key_points: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    insights: List[InsightItem] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ColumnStatistics(BaseModel):
    """Statistics for a single numeric or categorical column."""
    column_name: str
    data_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Optional[str] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    std_dev: Optional[float] = None


class DatasetAnalysisResponse(BaseModel):
    """Comprehensive analysis report for tabular datasets (CSV, Excel)."""
    asset_id: UUID
    filename: str
    mime_type: str
    total_rows: int
    total_columns: int
    missing_values_count: int
    duplicate_rows_count: int
    columns_summary: List[ColumnStatistics] = Field(default_factory=list)
    outliers_detected: List[Dict[str, Any]] = Field(default_factory=list)
    correlation_highlights: List[Dict[str, Any]] = Field(default_factory=list)
    executive_summary: str
    key_insights: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComparisonRequest(BaseModel):
    """Request payload to compare two assets."""
    asset_id_a: UUID
    asset_id_b: UUID


class ComparisonResponse(BaseModel):
    """Comparative analysis report between two assets."""
    asset_a_name: str
    asset_b_name: str
    asset_a_id: UUID
    asset_b_id: UUID
    similarity_score: float
    change_summary: str
    added_information: List[str] = Field(default_factory=list)
    removed_information: List[str] = Field(default_factory=list)
    common_sections: List[str] = Field(default_factory=list)
    differences: List[Dict[str, Any]] = Field(default_factory=list)
    compared_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnalysisReportExportRequest(BaseModel):
    """Request payload to export analysis report."""
    title: str
    format: str = Field("markdown", description="markdown, json, or pdf")
    summary: str
    insights: List[InsightItem] = Field(default_factory=list)
    statistics: Optional[Dict[str, Any]] = None


class AnalysisReportExportResponse(BaseModel):
    """Exported analysis report artifact."""
    title: str
    format: str
    content: str
    exported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
