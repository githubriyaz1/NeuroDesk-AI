import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from app.schemas.knowledge import Citation, RetrievedDocument


class ResultRanker:
    """Multi-factor ranker and deduplicator for knowledge retrieval results.
    
    Combines:
    1. Keyword relevance (0.35)
    2. Metadata match score (0.25)
    3. Asset recency (0.15)
    4. Asset priority (0.15)
    5. Conversation context relevance (0.10)
    """

    @staticmethod
    def calculate_score(
        doc: RetrievedDocument,
        query: str,
        conversation_context: Optional[str] = None,
    ) -> float:
        stopwords = {"the", "and", "this", "that", "what", "how", "are", "there", "for", "with", "show", "give", "tell", "explain", "many", "which", "does"}
        query_words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2 and w.lower() not in stopwords]
        doc_text = f"{doc.asset_name} {doc.content} {doc.section or ''}".lower()

        # 1. Keyword Relevance Score (0.35)
        if not query_words:
            keyword_score = 0.5
        else:
            matches = 0
            for w in query_words:
                stem = w.rstrip("s").rstrip("ing").rstrip("ed")
                if (len(stem) >= 3 and stem in doc_text) or w in doc_text:
                    matches += 1
            keyword_score = min(matches / len(query_words), 1.0)

        # 2. Metadata Score (0.25)
        metadata_score = 0.8 if doc.metadata else 0.4

        # 3. Recency Score (0.15)
        recency_score = 0.5
        if doc.created_at:
            now = datetime.now(timezone.utc)
            created = doc.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            days_old = max((now - created).days, 0)
            recency_score = max(1.0 - (days_old / 365.0), 0.1)

        # 4. Asset Priority Score (0.15)
        priority_score = doc.score if doc.score > 0 else 0.7

        # 5. Conversation Context Relevance Score (0.10)
        context_score = 0.5
        if conversation_context and any(w in conversation_context.lower() for w in query_words):
            context_score = 0.9

        final_score = (
            (keyword_score * 0.35)
            + (metadata_score * 0.25)
            + (recency_score * 0.15)
            + (priority_score * 0.15)
            + (context_score * 0.10)
        )
        return round(final_score, 4)

    def rank_and_deduplicate(
        self,
        documents: List[RetrievedDocument],
        query: str,
        conversation_context: Optional[str] = None,
        min_confidence: float = 0.1,
    ) -> List[RetrievedDocument]:
        """Calculates combined score, deduplicates by content/asset_id, and ranks descending."""
        seen_keys = set()
        deduped: List[RetrievedDocument] = []

        for doc in documents:
            key = f"{doc.asset_id}-{doc.section or ''}-{doc.content[:50]}"
            if key in seen_keys:
                continue
            seen_keys.add(key)

            doc.score = self.calculate_score(doc, query, conversation_context)
            if doc.score >= min_confidence:
                deduped.append(doc)

        deduped.sort(key=lambda d: d.score, reverse=True)
        return deduped

    @staticmethod
    def compress_context(documents: List[RetrievedDocument], max_characters: int = 4000) -> str:
        """Compresses top ranked documents into a single prompt context block."""
        context_blocks = []
        current_len = 0

        for idx, doc in enumerate(documents, start=1):
            block = f"[{idx}] Source: {doc.asset_name} ({doc.source_type.upper()}"
            if doc.page_number:
                block += f", Page {doc.page_number}"
            if doc.section:
                block += f", Section: {doc.section}"
            block += f")\nContent: {doc.content.strip()}\n"

            if current_len + len(block) > max_characters:
                break
            context_blocks.append(block)
            current_len += len(block)

        return "\n---\n".join(context_blocks)


result_ranker = ResultRanker()
