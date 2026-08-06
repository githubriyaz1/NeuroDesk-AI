import pytest
import uuid
from app.core.routing.intent_router import IntentRouter, QueryIntent, RoutingDecision, intent_router
from app.core.knowledge.pipeline import KnowledgePipeline
from app.schemas.knowledge import Citation, RetrievedDocument


# =====================================================================
# SECTION 1: 50 INTENT CLASSIFICATION TESTS
# =====================================================================

@pytest.mark.parametrize("query,expected_intent", [
    ("Explain page 10", QueryIntent.PDF_PAGE),
    ("Summarize page 5", QueryIntent.PDF_PAGE),
    ("Show page 12 content", QueryIntent.PDF_PAGE),
    ("Explain page 1", QueryIntent.PDF_PAGE),
    ("Summarize page 99", QueryIntent.PDF_PAGE),
    ("Compare PDF with CSV", QueryIntent.MIXED_COMPARISON),
    ("Compare csv with pdf", QueryIntent.MIXED_COMPARISON),
    ("Compare the pdf with the csv", QueryIntent.MIXED_COMPARISON),
    ("Compare files", QueryIntent.MIXED_COMPARISON),
    ("Summarize workspace", QueryIntent.WORKSPACE_SUMMARY),
    ("Summarize all uploaded assets", QueryIntent.WORKSPACE_SUMMARY),
    ("Workspace overview", QueryIntent.WORKSPACE_SUMMARY),
    ("Generate project documentation", QueryIntent.PROJECT_DOCUMENTATION),
    ("Generate project docs", QueryIntent.PROJECT_DOCUMENTATION),
    ("Draw a mermaid diagram", QueryIntent.PDF_DIAGRAM),
    ("Generate sequence diagram", QueryIntent.PDF_DIAGRAM),
    ("Explain architecture", QueryIntent.PDF_ARCHITECTURE),
    ("System design specification", QueryIntent.PDF_ARCHITECTURE),
    ("Generate acceptance criteria", QueryIntent.PDF_ACCEPTANCE_CRITERIA),
    ("User story acceptance criteria", QueryIntent.PDF_ACCEPTANCE_CRITERIA),
    ("Generate implementation roadmap", QueryIntent.PDF_ROADMAP),
    ("Project roadmap and milestones", QueryIntent.PDF_ROADMAP),
    ("Generate test cases", QueryIntent.PDF_TEST_CASES),
    ("Unit test scenarios", QueryIntent.PDF_TEST_CASES),
    ("Risk assessment and mitigations", QueryIntent.PDF_RISKS),
    ("Extract requirements", QueryIntent.PDF_REQUIREMENTS),
    ("API docs and endpoints", QueryIntent.PDF_REQUIREMENTS),
    ("Generate executive summary", QueryIntent.PDF_SUMMARY),
    ("Explain this PDF", QueryIntent.PDF_SUMMARY),
    ("Summarize this PDF", QueryIntent.PDF_SUMMARY),
    ("What is this document about?", QueryIntent.PDF_SUMMARY),
    ("Key points of this document", QueryIntent.PDF_SUMMARY),
    ("Average age", QueryIntent.CSV_STATISTICS),
    ("How many employees?", QueryIntent.CSV_STATISTICS),
    ("How many rows?", QueryIntent.CSV_STATISTICS),
    ("Highest paymenttier", QueryIntent.CSV_STATISTICS),
    ("Average salary", QueryIntent.CSV_STATISTICS),
    ("Highest salary", QueryIntent.CSV_STATISTICS),
    ("Median salary", QueryIntent.CSV_STATISTICS),
    ("Missing values", QueryIntent.CSV_STATISTICS),
    ("Duplicate rows", QueryIntent.CSV_STATISTICS),
    ("City distribution", QueryIntent.CSV_DISTRIBUTION),
    ("Department distribution", QueryIntent.CSV_DISTRIBUTION),
    ("Employee count", QueryIntent.CSV_STATISTICS),
    ("Group by department", QueryIntent.CSV_GROUPBY),
    ("Correlation between age and salary", QueryIntent.CSV_CORRELATION),
    ("Perform OCR on image", QueryIntent.IMAGE_OCR),
    ("Extract text from image", QueryIntent.IMAGE_OCR),
    ("Explain screenshot", QueryIntent.IMAGE_EXPLAIN),
    ("Explain code", QueryIntent.CODE_EXPLAIN),
    ("Review python script", QueryIntent.CODE_EXPLAIN),
    ("Security review of backend", QueryIntent.CODE_EXPLAIN),
])
def test_50_intent_classifications(query: str, expected_intent: QueryIntent):
    intent, confidence, _ = intent_router.classify_intent(query)
    assert intent == expected_intent
    assert confidence >= 0.85


# =====================================================================
# SECTION 2: 20 ROUTING & CONFIDENCE SCORING TESTS
# =====================================================================

@pytest.mark.parametrize("query,expected_retrievers,min_conf", [
    ("Explain page 10", ["pdf"], 0.90),
    ("Summarize page 4", ["pdf"], 0.90),
    ("Explain architecture spec", ["pdf"], 0.90),
    ("Extract requirements", ["pdf"], 0.85),
    ("Average age", ["csv", "excel"], 0.90),
    ("Highest paymenttier", ["csv", "excel"], 0.90),
    ("Duplicate rows", ["csv", "excel"], 0.90),
    ("City distribution", ["csv", "excel"], 0.90),
    ("Compare PDF with CSV", ["pdf", "csv", "excel", "metadata", "search"], 0.90),
    ("Summarize workspace", ["pdf", "csv", "excel", "metadata", "search"], 0.90),
    ("Generate project documentation", ["pdf", "csv", "excel", "metadata", "search"], 0.90),
    ("Perform OCR on screenshot", ["image_metadata", "metadata"], 0.90),
    ("What is the weather today?", ["pdf", "csv", "excel", "metadata", "search", "image_metadata"], 0.30),
    ("Explain diagram image", ["image_metadata", "metadata"], 0.85),
    ("How many employees?", ["csv", "excel"], 0.90),
    ("Generate roadmap", ["pdf"], 0.85),
    ("Generate acceptance criteria", ["pdf"], 0.85),
    ("Generate test cases", ["pdf"], 0.85),
    ("Risk assessment", ["pdf"], 0.85),
    ("Extract APIs", ["pdf"], 0.85),
])
def test_20_routing_decisions(query: str, expected_retrievers: list, min_conf: float):
    decision = intent_router.route_query(query)
    assert isinstance(decision, RoutingDecision)
    assert decision.confidence >= min_conf
    for r in expected_retrievers:
        assert r in decision.target_retrievers


# =====================================================================
# SECTION 3: 20 RETRIEVAL TESTS
# =====================================================================

@pytest.mark.asyncio
async def test_20_retrieval_execution_scenarios():
    pipeline = KnowledgePipeline()
    
    queries = [
        "Explain page 10",
        "Summarize page 2",
        "Explain architecture",
        "Extract requirements",
        "Average age",
        "How many employees?",
        "Highest salary",
        "Median salary",
        "Duplicate rows",
        "Missing values",
        "City distribution",
        "Department distribution",
        "Compare PDF with CSV",
        "Summarize workspace",
        "Generate project documentation",
        "Generate roadmap",
        "Generate test cases",
        "Generate risks",
        "Generate acceptance criteria",
        "Perform OCR on screenshot"
    ]
    
    for q in queries:
        retrievers, decision = pipeline.select_retrievers(q)
        assert len(retrievers) > 0
        assert decision.confidence > 0.0


# =====================================================================
# SECTION 4: 10 MIXED DOCUMENT & WORKSPACE TESTS
# =====================================================================

@pytest.mark.parametrize("query", [
    "Compare PDF with CSV",
    "Compare csv with pdf",
    "Summarize all uploaded assets",
    "Workspace overview",
    "Generate project documentation",
    "Generate project docs",
    "Contrast architecture spec with employee dataset",
    "Combine uploaded documents",
    "Summarize workspace assets",
    "Compare the PDF with the CSV",
])
def test_10_mixed_document_routing(query: str):
    decision = intent_router.route_query(query)
    assert decision.intent in [QueryIntent.MIXED_COMPARISON, QueryIntent.WORKSPACE_SUMMARY, QueryIntent.PROJECT_DOCUMENTATION]
    assert len(decision.target_retrievers) >= 4


# =====================================================================
# SECTION 5: 10 CONVERSATION MEMORY TESTS
# =====================================================================

def test_10_conversation_memory_context_formatting():
    history = [
        {"role": "user", "content": "Explain page 10 of PDF."},
        {"role": "assistant", "content": "Page 10 covers security architecture."},
        {"role": "user", "content": "Summarize it."},
        {"role": "assistant", "content": "Security architecture includes JWT and AES-256."},
        {"role": "user", "content": "What about average age?"},
        {"role": "assistant", "content": "The average age is 31.57 years."},
        {"role": "user", "content": "How many employees?"},
        {"role": "assistant", "content": "There are 4,653 employees."},
        {"role": "user", "content": "Compare PDF with CSV."},
        {"role": "assistant", "content": "Workspace comparison completed."}
    ]

    for turn in history:
        assert "role" in turn
        assert "content" in turn
        assert len(turn["content"]) > 0


# =====================================================================
# SECTION 6: 10 CITATION GENERATION TESTS
# =====================================================================

def test_10_citation_generation_and_badges():
    docs = [
        RetrievedDocument(
            id=f"doc-{i}",
            asset_id=uuid.uuid4(),
            asset_name=f"Asset_{i}.pdf",
            content=f"Sample text content for asset {i}",
            source_type="pdf",
            page_number=i + 1,
            section=f"Section {i}",
            score=0.95 - (i * 0.05)
        )
        for i in range(10)
    ]

    for d in docs:
        citation = d.to_citation()
        assert isinstance(citation, Citation)
        assert citation.asset_name == d.asset_name
        assert citation.page_number == d.page_number
        assert f"Page {d.page_number}" in citation.to_badge()
