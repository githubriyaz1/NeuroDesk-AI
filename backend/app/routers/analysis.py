from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.analysis import (
    AnalysisReportExportRequest,
    AnalysisReportExportResponse,
    ComparisonRequest,
    ComparisonResponse,
    DatasetAnalysisResponse,
    DocumentAnalysisResponse,
    InsightItem,
)
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/analysis", tags=["AI Data Analyst & Document Intelligence"])


@router.post("/document", response_model=DocumentAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_document(
    asset_id: UUID = Query(..., description="Target document asset ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyzes document content (PDF, TXT, Markdown) generating executive summaries, key points, and risks."""
    try:
        return await analysis_service.analyze_document(db, current_user.id, asset_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Document analysis failed: {str(e)}")


@router.post("/dataset", response_model=DatasetAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_dataset(
    asset_id: UUID = Query(..., description="Target dataset asset ID (CSV, Excel)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculates dataset row/column stats, missing values, duplicates, and column statistics."""
    try:
        return await analysis_service.analyze_dataset(db, current_user.id, asset_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Dataset analysis failed: {str(e)}")


@router.post("/compare", response_model=ComparisonResponse, status_code=status.HTTP_200_OK)
async def compare_assets(
    payload: ComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compares two assets generating similarity score, added/removed info, and section differences."""
    try:
        return await analysis_service.compare_assets(db, current_user.id, payload.asset_id_a, payload.asset_id_b)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Asset comparison failed: {str(e)}")


@router.post("/insights", response_model=List[InsightItem], status_code=status.HTTP_200_OK)
async def generate_insights(
    title: str = Query(..., description="Report title"),
    summary: str = Query(..., description="Content summary"),
    current_user: User = Depends(get_current_user),
):
    """Generates structured executive insights, risks, opportunities, and next steps."""
    return analysis_service.generate_insights(title, summary)


@router.post("/export", response_model=AnalysisReportExportResponse, status_code=status.HTTP_200_OK)
async def export_report(
    payload: AnalysisReportExportRequest,
    current_user: User = Depends(get_current_user),
):
    """Exports structured analysis report in Markdown, JSON, or PDF format."""
    return analysis_service.export_report(payload)
