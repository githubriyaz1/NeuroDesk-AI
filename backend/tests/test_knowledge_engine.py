import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.core.knowledge.engine import knowledge_engine
from app.core.knowledge.indexer import knowledge_indexer
from app.core.knowledge.pipeline import knowledge_pipeline
from app.core.knowledge.ranking import result_ranker
from app.core.knowledge.retrievers import (
    CSVRetriever,
    ExcelRetriever,
    FutureRetriever,
    ImageMetadataRetriever,
    MetadataRetriever,
    PDFRetriever,
    SearchRetriever,
)
from app.schemas.knowledge import KnowledgeQueryRequest, RetrievedDocument


def test_retriever_instantiation():
    pdf_r = PDFRetriever()
    csv_r = CSVRetriever()
    excel_r = ExcelRetriever()
    meta_r = MetadataRetriever()
    search_r = SearchRetriever()
    img_r = ImageMetadataRetriever()
    fut_r = FutureRetriever()

    assert pdf_r.retriever_type == "pdf"
    assert csv_r.retriever_type == "csv"
    assert excel_r.retriever_type == "excel"
    assert meta_r.retriever_type == "metadata"
    assert search_r.retriever_type == "search"
    assert img_r.retriever_type == "image_metadata"
    assert fut_r.retriever_type == "future_extension"


def test_result_ranker_scoring_and_deduplication():
    asset_id = uuid4()
    doc1 = RetrievedDocument(
        id="doc1",
        asset_id=asset_id,
        asset_name="Financial_Report_Q3.pdf",
        content="Q3 Net profit increased by 15% year over year.",
        source_type="pdf",
        page_number=3,
        section="Executive Summary",
        score=0.9,
    )
    doc2 = RetrievedDocument(
        id="doc1_dup",
        asset_id=asset_id,
        asset_name="Financial_Report_Q3.pdf",
        content="Q3 Net profit increased by 15% year over year.",
        source_type="pdf",
        page_number=3,
        section="Executive Summary",
        score=0.8,
    )

    ranked = result_ranker.rank_and_deduplicate([doc1, doc2], query="Q3 net profit")
    assert len(ranked) == 1
    assert ranked[0].score > 0

    compressed = result_ranker.compress_context(ranked)
    assert "Financial_Report_Q3.pdf" in compressed
    assert "Executive Summary" in compressed


def test_knowledge_indexer():
    asset_id = uuid4()
    item = knowledge_indexer.index_asset(
        asset_id=asset_id,
        asset_name="Sales_Data.csv",
        file_type="text/csv",
        extracted_text="Region,Sales,Quarter\nNorth,50000,Q3",
        metadata_fields={"rows": 100},
    )

    assert item.asset_name == "Sales_Data.csv"
    search_res = knowledge_indexer.search_index("Sales North")
    assert len(search_res) == 1
    assert search_res[0].asset_id == asset_id

    stats = knowledge_indexer.get_stats()
    assert stats["total_indexed_assets"] >= 1

    removed = knowledge_indexer.remove_asset(asset_id)
    assert removed is True


@pytest.mark.asyncio
async def test_knowledge_engine_query_and_diagnostics(async_client: AsyncClient, auth_headers: dict):
    # Test Diagnostics Endpoint
    diag_res = await async_client.get("/api/v1/knowledge/diagnostics", headers=auth_headers)
    assert diag_res.status_code == 200
    diag = diag_res.json()
    assert diag["status"] == "healthy"
    assert "pdf" in diag["active_retrievers"]
    assert "metadata" in diag["active_retrievers"]

    # Test Query Endpoint
    query_payload = {
        "query": "financial revenue reports",
        "limit": 5,
        "min_confidence": 0.0,
    }
    q_res = await async_client.post("/api/v1/knowledge/query", headers=auth_headers, json=query_payload)
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["query"] == "financial revenue reports"
    assert "documents" in q_data
    assert "citations" in q_data
    assert "packaged_context" in q_data

    # Test Index Trigger Endpoint
    idx_res = await async_client.post("/api/v1/knowledge/index", headers=auth_headers)
    assert idx_res.status_code == 200
    assert idx_res.json()["status"] == "success"
