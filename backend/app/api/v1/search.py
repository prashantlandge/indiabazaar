import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SuggestResponse,
    TrackClickRequest,
)
from app.services.intelligence.query_parser import parse_query
from app.services.intelligence.semantic_search import hybrid_search
from app.services.intelligence.ranking_engine import rank_results
from app.services.intelligence.suggestion_engine import get_suggestions, get_related_searches

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    search_id = uuid.uuid4()

    # Parse query intent
    parsed_intent = await parse_query(request.query)

    # Run hybrid search
    raw_results = await hybrid_search(db, parsed_intent, request.filters)

    # Rank and format results
    ranked_results, available_filters = await rank_results(
        raw_results, parsed_intent, request.filters
    )

    # Paginate
    start = (request.page - 1) * request.per_page
    end = start + request.per_page
    page_results = ranked_results[start:end]

    # Get related searches
    related = await get_related_searches(request.query, parsed_intent)

    return SearchResponse(
        query_understanding={
            "product": parsed_intent.product,
            "intent_parsed": parsed_intent.is_valid,
            "filters_applied": [
                f for f in [
                    f"Location: {parsed_intent.location_preference}" if parsed_intent.location_preference else None,
                    f"Certifications: {', '.join(parsed_intent.certifications_required)}" if parsed_intent.certifications_required else None,
                    f"Quality: {parsed_intent.quality_tier}" if parsed_intent.quality_tier else None,
                ]
                if f
            ],
            "expanded_to": parsed_intent.expanded_query or request.query,
        },
        results=page_results,
        total=len(ranked_results),
        related_searches=related,
        available_filters=available_filters,
        search_id=search_id,
    )


@router.get("/suggest", response_model=SuggestResponse)
async def suggest(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    suggestions = await get_suggestions(q, db)
    return SuggestResponse(suggestions=suggestions)


@router.post("/track-click")
async def track_click(data: TrackClickRequest, db: AsyncSession = Depends(get_db)):
    from app.models.search_log import SearchLog

    log = SearchLog(
        raw_query="click_track",
        clicked_supplier_id=data.supplier_id,
        session_id=str(data.search_id),
    )
    db.add(log)
    return {"status": "tracked"}
