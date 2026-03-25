import logging

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_log import SearchLog

logger = logging.getLogger(__name__)


async def log_search(
    db: AsyncSession,
    raw_query: str,
    parsed_intent: dict | None = None,
    result_count: int | None = None,
    session_id: str | None = None,
):
    """Log a search query for analytics."""
    log = SearchLog(
        raw_query=raw_query,
        parsed_intent=parsed_intent,
        result_count=result_count,
        session_id=session_id,
    )
    db.add(log)


async def get_popular_searches(db: AsyncSession, limit: int = 20) -> list[dict]:
    """Get most popular search queries."""
    result = await db.execute(
        select(SearchLog.raw_query, func.count(SearchLog.id).label("count"))
        .where(SearchLog.raw_query != "click_track")
        .group_by(SearchLog.raw_query)
        .order_by(text("count DESC"))
        .limit(limit)
    )
    return [{"query": r.raw_query, "count": r.count} for r in result.all()]
