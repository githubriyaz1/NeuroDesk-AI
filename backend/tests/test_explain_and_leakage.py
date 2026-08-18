import pytest
from app.core.routing.intent_router import QueryIntent, intent_router
from app.core.llm.mock_provider import MockProvider
from app.core.llm.base import ProviderRequest

FORBIDDEN_LEAKAGE_STRINGS = [
    "Conversation History:",
    "User Question:",
    "Assistant:",
    "system prompt",
    "[FILE_PATH:",
    "Context Assessment",
    "Operational Guidelines",
]

@pytest.fixture
def mock_provider():
    return MockProvider()

def test_explain_intent_with_pdf(mock_provider):
    q_list = [
        "Explain",
        "Explain this",
        "Explain this PDF",
        "Explain the pdf",
        "Explain this document",
        "What is this PDF about?",
        "Summarize this PDF",
        "Give me an explanation",
        "Help me understand this PDF",
    ]
    for q in q_list:
        intent, confidence, _ = intent_router.classify_intent(q, attached_asset_types=["pdf"])
        assert intent == QueryIntent.PDF_SUMMARY, f"Query '{q}' failed to resolve to PDF_SUMMARY!"
        assert confidence >= 0.85

def test_explain_intent_with_csv(mock_provider):
    intent, confidence, _ = intent_router.classify_intent("Explain", attached_asset_types=["csv"])
    assert intent == QueryIntent.CSV_STATISTICS, "Explain with only CSV attached should resolve to CSV_STATISTICS!"

def test_pdf_plus_csv_isolation():
    # 1. Explain page 1 -> PDF
    intent1, _, _ = intent_router.classify_intent("Explain page 1", attached_asset_types=["pdf", "csv"])
    assert intent1 == QueryIntent.PDF_PAGE

    # 2. How many employees -> CSV
    intent2, _, _ = intent_router.classify_intent("How many employees?", attached_asset_types=["pdf", "csv"])
    assert intent2 == QueryIntent.CSV_STATISTICS

    # 3. Compare PDF with CSV -> MIXED
    intent3, _, _ = intent_router.classify_intent("Compare the PDF with the CSV", attached_asset_types=["pdf", "csv"])
    assert intent3 == QueryIntent.MIXED_COMPARISON

@pytest.mark.asyncio
async def test_no_assets_explain_no_leakage(mock_provider):
    req = ProviderRequest(prompt="Conversation History:\nUser: Explain\nAssistant:\n\nUser Question: Explain")
    res = await mock_provider.generate_response(req)
    for forbidden in FORBIDDEN_LEAKAGE_STRINGS:
        assert forbidden not in res.content, f"Forbidden leakage string '{forbidden}' found in no-assets response!"
    assert "No workspace document is currently attached" in res.content

@pytest.mark.asyncio
async def test_pdf_explanation_grounded(mock_provider):
    req = ProviderRequest(
        prompt="Explain this PDF",
        system_prompt="[Enterprise Knowledge Engine Retracted Sources]:\nPDF Document 'Architecture_Spec.pdf' [Page 1]:\nSystem Architecture details.\n\nPlease use the above sources..."
    )
    res = await mock_provider.generate_response(req)
    for forbidden in FORBIDDEN_LEAKAGE_STRINGS:
        assert forbidden not in res.content, f"Forbidden leakage string '{forbidden}' found in PDF response!"
    assert "PDF Explanation & Analysis" in res.content or "Architecture_Spec.pdf" in res.content
