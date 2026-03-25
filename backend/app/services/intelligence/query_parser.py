import hashlib
import json
import logging

import anthropic

from app.core.config import get_settings
from app.core.redis import get_redis
from app.schemas.search import ParsedIntent

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are a B2B procurement intelligence engine. Parse the buyer's query and extract structured procurement intent.

Return ONLY valid JSON with these fields:
- product: string (canonical product name)
- category: string (broad category)
- quantity: {value: number|null, unit: string|null}
- quality_tier: string (food_grade|industrial|premium|standard|null)
- certifications_required: string[] (ISO|CE|BIS|FSSAI|GMP|null)
- location_preference: string|null (city or state)
- urgency: string (high|medium|low|null)
- price_sensitivity: string (high|medium|low|null) based on language cues
- buyer_type: string (manufacturer|trader|retailer|individual|null)
- semantic_tags: string[] (5-10 related terms, synonyms, applications)
- expanded_query: string (enriched query for semantic search, include synonyms and related terms)
- is_valid: boolean (false if query is not a procurement request)

Examples of semantic expansion:
- "corrugated boxes" → also: carton, packaging, cardboard, shipping box, mailer
- "SS pipe" → also: stainless steel pipe, tube, 304 grade, 316 grade, seamless
- "transformer oil" → also: mineral insulating oil, electrical insulating oil, dielectric fluid"""


async def parse_query(query: str) -> ParsedIntent:
    """Parse a natural language procurement query into structured intent using Claude API."""
    # Check Redis cache first
    cache_key = f"intent:{hashlib.md5(query.lower().strip().encode()).hexdigest()}"
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return ParsedIntent(**json.loads(cached))
    except Exception:
        logger.warning("Redis cache unavailable for query parsing")

    # If no API key, fallback to keyword-based parsing
    if not settings.ANTHROPIC_API_KEY:
        return _fallback_parse(query)

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": query}],
        )

        content = response.content[0].text
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        parsed = json.loads(content)
        intent = ParsedIntent(**parsed)

        # Cache the result
        try:
            redis = await get_redis()
            await redis.set(
                cache_key,
                intent.model_dump_json(),
                ex=settings.QUERY_CACHE_TTL_SECONDS,
            )
        except Exception:
            pass

        return intent

    except Exception as e:
        logger.error(f"LLM query parsing failed: {e}")
        return _fallback_parse(query)


def _fallback_parse(query: str) -> ParsedIntent:
    """Simple keyword-based fallback when LLM is unavailable."""
    words = query.lower().split()

    # Extract location hints (Indian states/cities)
    locations = {
        "maharashtra", "mumbai", "pune", "delhi", "bangalore", "bengaluru",
        "chennai", "kolkata", "hyderabad", "ahmedabad", "gujarat", "tamil nadu",
        "karnataka", "rajasthan", "jaipur", "lucknow", "uttar pradesh",
        "west bengal", "kerala", "madhya pradesh", "indore", "bhopal",
        "noida", "gurgaon", "chandigarh", "punjab", "haryana", "surat",
    }
    location = None
    for w in words:
        if w in locations:
            location = w.title()
            break

    # Extract certifications
    cert_keywords = {"iso", "ce", "bis", "fssai", "gmp", "haccp"}
    certs = [w.upper() for w in words if w.lower() in cert_keywords]

    # Urgency detection
    urgency = None
    if any(w in words for w in ["urgent", "asap", "immediately", "rush"]):
        urgency = "high"

    # Quality tier
    quality = None
    if any(w in query.lower() for w in ["food grade", "food-grade"]):
        quality = "food_grade"
    elif any(w in words for w in ["premium", "high-quality"]):
        quality = "premium"
    elif any(w in words for w in ["industrial"]):
        quality = "industrial"

    # Product: everything that's not a filter keyword
    filter_words = locations | cert_keywords | {"urgent", "asap", "need", "want", "require",
                                                  "kg", "ton", "pieces", "bulk", "order"}
    product_words = [w for w in words if w not in filter_words and len(w) > 1]
    product = " ".join(product_words).strip() or query

    return ParsedIntent(
        product=product,
        category=None,
        quantity=None,
        quality_tier=quality,
        certifications_required=certs,
        location_preference=location,
        urgency=urgency,
        price_sensitivity=None,
        buyer_type=None,
        semantic_tags=product_words[:10],
        expanded_query=query,
        is_valid=len(product_words) > 0,
    )
