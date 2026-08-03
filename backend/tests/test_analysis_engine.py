import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis import (
    analysis_engine,
    comparison_engine,
    dataset_analyzer,
    document_analyzer,
    insight_generator,
    recommendation_engine,
    statistics_engine,
    summary_engine,
)
from app.services.analysis_service import analysis_service


@pytest.mark.asyncio
async def test_statistics_engine():
    stats = statistics_engine.calculate_numeric_stats([10.0, 20.0, 30.0, 40.0, 50.0])
    assert stats["mean"] == 30.0
    assert stats["median"] == 30.0
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0

    col_stat = statistics_engine.analyze_column("revenue", [100.0, 200.0, None, 400.0])
    assert col_stat.column_name == "revenue"
    assert col_stat.null_count == 1
    assert col_stat.data_type == "numeric"


@pytest.mark.asyncio
async def test_summary_engine():
    text = "NeuroDesk AI is an enterprise workspace. It provides RAG knowledge retrieval and document intelligence."
    summary = summary_engine.generate_executive_summary(text, "test.pdf")
    assert "NeuroDesk AI" in summary

    pts = summary_engine.extract_key_points(text, max_points=2)
    assert len(pts) > 0

    keywords = summary_engine.extract_keywords(text)
    assert len(keywords) > 0


@pytest.mark.asyncio
async def test_document_analyzer():
    res = document_analyzer.analyze_document(
        asset_id=uuid4(),
        filename="Report.pdf",
        mime_type="application/pdf",
        text_content="Q3 Financial growth increased 25% year over year.",
    )
    assert res.filename == "Report.pdf"
    assert len(res.key_points) > 0
    assert len(res.insights) > 0


@pytest.mark.asyncio
async def test_dataset_analyzer():
    res = dataset_analyzer.analyze_dataset(
        asset_id=uuid4(),
        filename="Sales.csv",
        mime_type="text/csv",
        columns=["ID", "Amount"],
        rows_data=[[1, 100], [2, None], [3, 300]],
    )
    assert res.filename == "Sales.csv"
    assert res.total_rows == 3
    assert res.total_columns == 2
    assert res.missing_values_count == 1


@pytest.mark.asyncio
async def test_comparison_engine():
    res = comparison_engine.compare_texts(
        asset_a_id=uuid4(),
        asset_a_name="DocA.txt",
        text_a="Alpha Beta Gamma",
        asset_b_id=uuid4(),
        asset_b_name="DocB.txt",
        text_b="Alpha Beta Delta",
    )
    assert res.asset_a_name == "DocA.txt"
    assert res.asset_b_name == "DocB.txt"
    assert res.similarity_score > 0.0


@pytest.mark.asyncio
async def test_insight_generator_and_recommendation():
    insights = insight_generator.generate_comprehensive_insights("Title", "Summary text")
    assert len(insights) >= 5

    recs = recommendation_engine.generate_recommendations("pdf", missing_count=3, duplicate_count=1)
    assert len(recs) >= 3


@pytest.mark.asyncio
async def test_analysis_intent_detection():
    intent1 = analysis_service.detect_analysis_intent("Summarize this PDF document")
    assert intent1["intent_type"] == "summary"

    intent2 = analysis_service.detect_analysis_intent("Which CSV column has missing values?")
    assert intent2["intent_type"] == "dataset_analysis"

    intent3 = analysis_service.detect_analysis_intent("Compare these two resumes")
    assert intent3["intent_type"] == "compare"


@pytest.mark.asyncio
async def test_analysis_api_endpoints(async_client: AsyncClient, auth_headers: dict):
    # Test POST /api/v1/analysis/insights
    resp_ins = await async_client.post(
        "/api/v1/analysis/insights?title=ExecutiveReport&summary=Growth+Report",
        headers=auth_headers,
    )
    assert resp_ins.status_code == 200
    assert len(resp_ins.json()) >= 5

    # Test POST /api/v1/analysis/export
    payload = {
        "title": "Quarterly Report",
        "format": "markdown",
        "summary": "Revenue increased by 15%.",
        "insights": [
            {
                "category": "executive_summary",
                "title": "Overview",
                "description": "Positive growth trajectory.",
                "impact_level": "high",
                "confidence_score": 0.95,
            }
        ],
    }
    resp_exp = await async_client.post(
        "/api/v1/analysis/export",
        json=payload,
        headers=auth_headers,
    )
    assert resp_exp.status_code == 200
    assert "Quarterly Report" in resp_exp.json()["content"]
