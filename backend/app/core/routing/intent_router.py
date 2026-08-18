import re
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from pydantic import BaseModel, Field
from app.core.logging import logger


class QueryIntent(str, Enum):
    # PDF / Document Intents
    PDF_PAGE = "PDF_PAGE"
    PDF_SUMMARY = "PDF_SUMMARY"
    PDF_ARCHITECTURE = "PDF_ARCHITECTURE"
    PDF_REQUIREMENTS = "PDF_REQUIREMENTS"
    PDF_ROADMAP = "PDF_ROADMAP"
    PDF_ACCEPTANCE_CRITERIA = "PDF_ACCEPTANCE_CRITERIA"
    PDF_TEST_CASES = "PDF_TEST_CASES"
    PDF_RISKS = "PDF_RISKS"
    PDF_API_DOCS = "PDF_API_DOCS"
    PDF_DIAGRAM = "PDF_DIAGRAM"

    # CSV / Excel / Tabular Intents
    CSV_STATISTICS = "CSV_STATISTICS"
    CSV_DISTRIBUTION = "CSV_DISTRIBUTION"
    CSV_FILTER = "CSV_FILTER"
    CSV_GROUPBY = "CSV_GROUPBY"
    CSV_CORRELATION = "CSV_CORRELATION"

    # Image Intents
    IMAGE_OCR = "IMAGE_OCR"
    IMAGE_EXPLAIN = "IMAGE_EXPLAIN"

    # Code Intents
    CODE_EXPLAIN = "CODE_EXPLAIN"
    CODE_REVIEW = "CODE_REVIEW"
    CODE_SECURITY = "CODE_SECURITY"
    CODE_GENERATE = "CODE_GENERATE"

    # Multi-Asset / Hybrid Workspace Intents
    MIXED_COMPARISON = "MIXED_COMPARISON"
    WORKSPACE_SUMMARY = "WORKSPACE_SUMMARY"
    PROJECT_DOCUMENTATION = "PROJECT_DOCUMENTATION"
    GENERAL_QUERY = "GENERAL_QUERY"


class RoutingDecision(BaseModel):
    query: str
    intent: QueryIntent
    confidence: float
    target_retrievers: List[str]
    target_page: Optional[int] = None
    target_asset_types: List[str] = Field(default_factory=list)
    routing_latency_ms: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentRouter:
    """Enterprise Hybrid RAG Intent Router & Scorer.
    Classifies queries before retrieval and assigns confidence scores to target retrievers.
    """

    def classify_intent(
        self, query: str, attached_asset_types: Optional[List[str]] = None
    ) -> Tuple[QueryIntent, float, Optional[int]]:
        clean_q = query
        if "User Question:" in query:
            clean_q = query.split("User Question:")[-1]
        q_lower = clean_q.lower().strip()

        # 1. Page Specific Queries (e.g. "Explain page 10", "Summarize page 5")
        page_match = re.search(r"\bpage\s*(\d+)\b", q_lower)
        if page_match:
            page_num = int(page_match.group(1))
            return QueryIntent.PDF_PAGE, 0.98, page_num

        # 2. Mixed Asset / Workspace Comparison Queries
        if any(k in q_lower for k in ["compare pdf with csv", "compare csv with pdf", "compare the pdf with the csv", "compare files", "contrast", "combine uploaded", "combine documents", "pdf vs csv"]):
            return QueryIntent.MIXED_COMPARISON, 0.95, None
        if any(k in q_lower for k in ["summarize workspace", "summarize all uploaded assets", "all assets", "workspace overview", "all documents"]):
            return QueryIntent.WORKSPACE_SUMMARY, 0.92, None
        if any(k in q_lower for k in ["generate project documentation", "generate project docs", "project docs", "system documentation"]):
            return QueryIntent.PROJECT_DOCUMENTATION, 0.90, None

        # 3. Image & OCR Intents (Evaluated BEFORE general text matching)
        if any(k in q_lower for k in ["ocr", "extract text from image"]):
            return QueryIntent.IMAGE_OCR, 0.95, None
        if any(k in q_lower for k in ["explain screenshot", "explain diagram image", "explain ui", "screenshot"]):
            return QueryIntent.IMAGE_EXPLAIN, 0.90, None

        # 4. Code Intents (Evaluated BEFORE general text matching)
        if any(k in q_lower for k in ["security review", "code review", "python script", "review code", "explain code", "code analysis", "optimize code"]):
            return QueryIntent.CODE_EXPLAIN, 0.90, None

        # 5. CSV / Tabular Operations Intents
        if any(k in q_lower for k in [
            "how many rows", "row count", "number of rows", "total rows", "how many employees", "employee count",
            "average age", "mean employee age", "highest salary", "median salary", "average salary", "lowest salary",
            "lowest salaries", "top 5 salaries", "top 5", "top 10", "bottom 5", "bottom 10", "missing values",
            "duplicate rows", "paymenttier", "highest paymenttier", "people work here", "who earns the most",
            "salary stats", "break employees down", "people are based", "earning above", "greater than", "less than",
            "above 80k", "highest average salary", "which department", "which city", "most employees", "experience",
            "joined after", "joining year", "joiningyear", "average experience", "what about engineering", "and bangalore"
        ]):
            return QueryIntent.CSV_STATISTICS, 0.98, None
        if any(k in q_lower for k in ["city distribution", "department distribution", "distribution", "breakdown"]):
            return QueryIntent.CSV_DISTRIBUTION, 0.95, None
        if any(k in q_lower for k in ["group by", "grouped", "pivot"]):
            return QueryIntent.CSV_GROUPBY, 0.90, None
        if any(k in q_lower for k in ["correlation", "trend", "histogram"]):
            return QueryIntent.CSV_CORRELATION, 0.90, None

        # 6. Natural Document Explanation Intents ("explain", "explain this pdf", "what is this document about", etc.)
        doc_explanation_phrases = {
            "explain",
            "explain this",
            "explain this pdf",
            "explain the pdf",
            "explain pdf",
            "explain document",
            "explain the document",
            "explain this document",
            "what is this pdf about",
            "what is this document about",
            "what is this file about",
            "summarize this pdf",
            "summarize the document",
            "summarize this document",
            "summarize pdf",
            "give me an explanation",
            "help me understand this pdf",
            "help me understand this document",
            "help me understand this",
            "summarize this",
            "summary of this pdf",
            "summary of document",
            "summarize",
        }
        clean_q_nopunct = re.sub(r"[^\w\s]", "", q_lower).strip()
        if clean_q_nopunct in doc_explanation_phrases or q_lower in doc_explanation_phrases:
            if attached_asset_types and "csv" in attached_asset_types and "pdf" not in attached_asset_types and "document" not in attached_asset_types:
                return QueryIntent.CSV_STATISTICS, 0.95, None
            return QueryIntent.PDF_SUMMARY, 0.95, None

        # 7. PDF Reasoning Intents
        if any(k in q_lower for k in ["mermaid", "sequence diagram", "uml", "flowchart"]):
            return QueryIntent.PDF_DIAGRAM, 0.95, None
        if any(k in q_lower for k in ["architecture", "system design", "component diagram"]):
            return QueryIntent.PDF_ARCHITECTURE, 0.92, None
        if any(k in q_lower for k in ["acceptance criteria", "user story"]):
            return QueryIntent.PDF_ACCEPTANCE_CRITERIA, 0.92, None
        if any(k in q_lower for k in ["roadmap", "milestone", "implementation plan"]):
            return QueryIntent.PDF_ROADMAP, 0.90, None
        if any(k in q_lower for k in ["test case", "test scenarios", "unit test scenario"]):
            return QueryIntent.PDF_TEST_CASES, 0.90, None
        if any(k in q_lower for k in ["risk", "vulnerability", "mitigation"]):
            return QueryIntent.PDF_RISKS, 0.90, None
        if any(k in q_lower for k in ["extract requirements", "requirement", "api docs", "extract apis", "endpoint"]):
            return QueryIntent.PDF_REQUIREMENTS, 0.90, None
        if any(k in q_lower for k in ["executive summary", "executive brief"]):
            return QueryIntent.PDF_SUMMARY, 0.92, None

        # General Document Query
        if any(k in q_lower for k in ["pdf", "document", "file"]):
            return QueryIntent.PDF_SUMMARY, 0.85, None

        return QueryIntent.GENERAL_QUERY, 0.40, None

    def route_query(
        self,
        query: str,
        requested_types: Optional[List[str]] = None,
        attached_asset_types: Optional[List[str]] = None,
    ) -> RoutingDecision:
        start_time = time.time()
        intent, confidence, target_page = self.classify_intent(query, attached_asset_types)

        # Select target retrievers based on confidence scoring rules
        target_retrievers: List[str] = []
        target_asset_types: List[str] = []

        if requested_types:
            target_retrievers = requested_types
            confidence = 1.0
        else:
            if intent in [
                QueryIntent.PDF_PAGE,
                QueryIntent.PDF_SUMMARY,
                QueryIntent.PDF_ARCHITECTURE,
                QueryIntent.PDF_REQUIREMENTS,
                QueryIntent.PDF_ROADMAP,
                QueryIntent.PDF_ACCEPTANCE_CRITERIA,
                QueryIntent.PDF_TEST_CASES,
                QueryIntent.PDF_RISKS,
                QueryIntent.PDF_API_DOCS,
                QueryIntent.PDF_DIAGRAM,
            ]:
                if confidence > 0.8:
                    target_retrievers = ["pdf"]
                else:
                    target_retrievers = ["pdf", "metadata", "search"]
                target_asset_types = ["pdf", "document"]

            elif intent in [
                QueryIntent.CSV_STATISTICS,
                QueryIntent.CSV_DISTRIBUTION,
                QueryIntent.CSV_FILTER,
                QueryIntent.CSV_GROUPBY,
                QueryIntent.CSV_CORRELATION,
            ]:
                if confidence > 0.8:
                    target_retrievers = ["csv", "excel"]
                else:
                    target_retrievers = ["csv", "excel", "metadata"]
                target_asset_types = ["csv", "excel", "spreadsheet"]

            elif intent in [QueryIntent.IMAGE_OCR, QueryIntent.IMAGE_EXPLAIN]:
                target_retrievers = ["image_metadata", "metadata"]
                target_asset_types = ["image"]

            elif intent in [QueryIntent.MIXED_COMPARISON, QueryIntent.WORKSPACE_SUMMARY, QueryIntent.PROJECT_DOCUMENTATION]:
                # Multi-retriever execution across workspace
                target_retrievers = ["pdf", "csv", "excel", "metadata", "search"]
                target_asset_types = ["pdf", "csv", "excel", "image", "document"]

            else:
                # Hybrid retrieval across all indexed assets
                target_retrievers = ["pdf", "csv", "excel", "metadata", "search", "image_metadata"]
                target_asset_types = []

        latency_ms = round((time.time() - start_time) * 1000, 2)

        decision = RoutingDecision(
            query=query,
            intent=intent,
            confidence=confidence,
            target_retrievers=target_retrievers,
            target_page=target_page,
            target_asset_types=target_asset_types,
            routing_latency_ms=latency_ms,
        )

        logger.info(
            f"[INTENT_ROUTER] Query: '{query[:40]}' | Intent: {decision.intent.value} | "
            f"Confidence: {decision.confidence:.2f} | Retrievers: {decision.target_retrievers} | "
            f"Page: {decision.target_page} | Latency: {decision.routing_latency_ms}ms"
        )
        return decision


intent_router = IntentRouter()
