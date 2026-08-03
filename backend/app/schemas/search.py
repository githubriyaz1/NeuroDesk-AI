from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.asset import AssetDetailResponse


class ParsedQuerySchema(BaseModel):
    free_text: str = ""
    asset_type: Optional[str] = None
    is_favorite: Optional[bool] = None
    status: Optional[str] = None
    min_size_bytes: Optional[int] = None
    max_size_bytes: Optional[int] = None
    created_after: Optional[datetime] = None
    name_filter: Optional[str] = None


class SearchResultItemSchema(BaseModel):
    asset: AssetDetailResponse
    match_score: float = 1.0
    matched_fields: List[str] = []


class SearchResponse(BaseModel):
    items: List[SearchResultItemSchema]
    total: int
    page: int
    page_size: int
    total_pages: int
    parsed_query: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class SearchSuggestionSchema(BaseModel):
    text: str
    type: str  # "filename", "metadata", "type", "tag"


class SearchSuggestionsResponse(BaseModel):
    suggestions: List[SearchSuggestionSchema]


SearchQueryRequest = ParsedQuerySchema
SearchResultResponse = SearchResponse
QuickSuggestionResponse = SearchSuggestionsResponse
