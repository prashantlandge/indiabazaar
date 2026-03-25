from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.supplier import SupplierSearchResult


class SearchFilters(BaseModel):
    city: list[str] | None = None
    state: list[str] | None = None
    verified_only: bool = False
    min_trust_score: int = 0
    certifications: list[str] | None = None
    nature_of_business: list[str] | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    filters: SearchFilters = SearchFilters()


class QueryUnderstanding(BaseModel):
    product: str | None = None
    intent_parsed: bool = True
    filters_applied: list[str] = []
    expanded_to: str | None = None


class FilterOption(BaseModel):
    value: str
    count: int


class AvailableFilters(BaseModel):
    cities: list[FilterOption] = []
    certifications: list[FilterOption] = []
    nature_of_business: list[FilterOption] = []
    states: list[FilterOption] = []


class SearchResponse(BaseModel):
    query_understanding: QueryUnderstanding
    results: list[SupplierSearchResult]
    total: int
    related_searches: list[str] = []
    available_filters: AvailableFilters = AvailableFilters()
    search_id: UUID


class SuggestionItem(BaseModel):
    text: str
    type: str
    count: int = 0


class SuggestResponse(BaseModel):
    suggestions: list[SuggestionItem]


class TrackClickRequest(BaseModel):
    search_id: UUID
    supplier_id: UUID
    position: int


class ParsedIntent(BaseModel):
    product: str | None = None
    category: str | None = None
    quantity: dict | None = None
    quality_tier: str | None = None
    certifications_required: list[str] = []
    location_preference: str | None = None
    urgency: str | None = None
    price_sensitivity: str | None = None
    buyer_type: str | None = None
    semantic_tags: list[str] = []
    expanded_query: str = ""
    is_valid: bool = True
