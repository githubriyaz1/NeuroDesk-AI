from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.search_repository import search_repository
from app.schemas.asset import AssetDetailResponse
from app.schemas.search import (
    SearchResponse,
    SearchResultItemSchema,
    SearchSuggestionSchema,
    SearchSuggestionsResponse,
)
from app.services.query_parser import query_parser


class SearchService:
    """Enterprise Business Logic Service for Search Platform."""

    async def search(
        self,
        db: AsyncSession,
        user_id: UUID,
        q: str,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> SearchResponse:
        """Executes full search pipeline: parses syntax, queries repository, ranks results."""
        page = max(1, page)
        page_size = min(max(1, page_size), 100)

        parsed = query_parser.parse(q)
        assets, total = await search_repository.search_assets(
            db=db,
            user_id=user_id,
            parsed=parsed,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        free_text = (parsed.get("free_text") or "").lower()
        items = []
        for asset in assets:
            matched_fields = []
            score = 1.0

            if free_text:
                if free_text in asset.name.lower():
                    matched_fields.append("name")
                    score += 0.5
                if free_text in asset.original_filename.lower():
                    matched_fields.append("original_filename")
                    score += 0.3
                if asset.description and free_text in asset.description.lower():
                    matched_fields.append("description")
                    score += 0.2

            items.append(
                SearchResultItemSchema(
                    asset=AssetDetailResponse.model_validate(asset),
                    match_score=score,
                    matched_fields=matched_fields if matched_fields else ["filter"],
                )
            )

        total_pages = max(1, (total + page_size - 1) // page_size)

        return SearchResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            parsed_query=parsed,
        )

    async def get_suggestions(
        self, db: AsyncSession, user_id: UUID, q: str, limit: int = 8
    ) -> SearchSuggestionsResponse:
        """Retrieves search auto-complete suggestions from asset titles and metadata values."""
        raw_suggestions = await search_repository.get_suggestions(
            db=db, user_id=user_id, query_prefix=q, limit=limit
        )

        return SearchSuggestionsResponse(
            suggestions=[SearchSuggestionSchema(**s) for s in raw_suggestions]
        )


search_service = SearchService()
