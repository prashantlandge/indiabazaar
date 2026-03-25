import json
import logging

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.models.product import Product
from app.models.search_log import SearchLog
from app.models.supplier import Supplier
from app.schemas.search import ParsedIntent, SuggestionItem

logger = logging.getLogger(__name__)
settings = get_settings()


async def get_suggestions(query: str, db: AsyncSession) -> list[SuggestionItem]:
    """
    Real-time autocomplete suggestions from:
    1. Popular search queries
    2. Product names
    3. Supplier company names
    """
    q = query.lower().strip()
    if len(q) < 2:
        return []

    # Try cache first
    cache_key = f"suggest:{q}"
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return [SuggestionItem(**s) for s in json.loads(cached)]
    except Exception:
        pass

    suggestions = []

    # 1. Popular queries from search logs
    log_results = await db.execute(
        select(SearchLog.raw_query, func.count(SearchLog.id).label("cnt"))
        .where(
            SearchLog.raw_query.ilike(f"%{q}%"),
            SearchLog.raw_query != "click_track",
        )
        .group_by(SearchLog.raw_query)
        .order_by(text("cnt DESC"))
        .limit(5)
    )
    for row in log_results.all():
        suggestions.append(SuggestionItem(text=row.raw_query, type="search", count=row.cnt))

    # 2. Product name matches
    product_results = await db.execute(
        select(Product.name, func.count(Product.id).label("cnt"))
        .where(Product.name.ilike(f"%{q}%"))
        .group_by(Product.name)
        .order_by(text("cnt DESC"))
        .limit(5)
    )
    for row in product_results.all():
        suggestions.append(SuggestionItem(text=row.name, type="product", count=row.cnt))

    # 3. Company name matches
    supplier_results = await db.execute(
        select(Supplier.company_name)
        .where(Supplier.company_name.ilike(f"%{q}%"))
        .order_by(Supplier.trust_score.desc())
        .limit(3)
    )
    for row in supplier_results.all():
        suggestions.append(SuggestionItem(text=row.company_name, type="supplier", count=0))

    # Deduplicate and limit
    seen = set()
    unique = []
    for s in suggestions:
        key = s.text.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    suggestions = unique[:10]

    # Cache for 5 minutes
    try:
        redis = await get_redis()
        await redis.set(cache_key, json.dumps([s.model_dump() for s in suggestions]), ex=300)
    except Exception:
        pass

    return suggestions


async def get_related_searches(query: str, intent: ParsedIntent) -> list[str]:
    """Generate related search suggestions based on the current query."""
    cache_key = f"related:{query.lower().strip()}"

    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    # Try LLM-based generation
    if settings.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": f"Given a B2B procurement search for \"{query}\", suggest 5 related procurement searches. Return ONLY a JSON array of strings.",
                }],
            )
            content = response.content[0].text
            if "[" in content:
                content = content[content.index("["):content.rindex("]") + 1]
            related = json.loads(content)[:5]

            try:
                redis = await get_redis()
                await redis.set(cache_key, json.dumps(related), ex=settings.SUGGESTION_CACHE_TTL_SECONDS)
            except Exception:
                pass

            return related
        except Exception as e:
            logger.warning(f"Related searches LLM call failed: {e}")

    # Fallback: use semantic tags from intent
    if intent.semantic_tags:
        return intent.semantic_tags[:5]

    return []
