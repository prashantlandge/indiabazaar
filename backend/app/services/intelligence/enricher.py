import json
import logging

import anthropic

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

CITY_NORMALIZATION = {
    "bombay": "Mumbai", "calcutta": "Kolkata", "madras": "Chennai",
    "bangalore": "Bengaluru", "baroda": "Vadodara", "trivandrum": "Thiruvananthapuram",
    "pondicherry": "Puducherry", "benares": "Varanasi", "poona": "Pune",
    "cochin": "Kochi", "calicut": "Kozhikode", "mangalore": "Mangaluru",
    "mysore": "Mysuru", "shimoga": "Shivamogga", "belgaum": "Belagavi",
    "hubli": "Hubballi", "gulbarga": "Kalaburagi",
}

CATEGORY_TAXONOMY = [
    "Raw Materials", "Machinery & Equipment", "Consumer Goods", "Chemicals",
    "Textiles & Apparel", "Electronics & Electrical", "Food & Beverages",
    "Construction & Building", "Packaging", "Automotive", "Agriculture",
    "Pharmaceuticals", "Metals & Minerals", "Plastics & Polymers",
    "Paper & Printing", "Furniture & Furnishing", "Safety & Security",
    "IT & Software", "Healthcare", "Industrial Supplies",
]


def normalize_city(city: str | None) -> str | None:
    """Normalize city name to standard form."""
    if not city:
        return None
    return CITY_NORMALIZATION.get(city.lower().strip(), city.strip().title())


async def classify_category(product_names: list[str], description: str | None = None) -> dict:
    """Use Claude to classify supplier into category/subcategory."""
    if not settings.ANTHROPIC_API_KEY:
        return {"primary_category": None, "subcategory": None}

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = f"""Classify this B2B supplier into a category.

Products: {', '.join(product_names[:10])}
Description: {description or 'N/A'}

Available categories: {', '.join(CATEGORY_TAXONOMY)}

Return ONLY JSON: {{"primary_category": "...", "subcategory": "..."}}"""

        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=128,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text
        if "{" in content:
            content = content[content.index("{"):content.rindex("}") + 1]
        return json.loads(content)
    except Exception as e:
        logger.error(f"Category classification failed: {e}")
        return {"primary_category": None, "subcategory": None}


async def generate_description(supplier_data: dict) -> str | None:
    """Generate a factual description for suppliers with missing/short descriptions."""
    if not settings.ANTHROPIC_API_KEY:
        return None

    try:
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = f"""Generate a brief, factual 1-2 sentence B2B company description.

Company: {supplier_data.get('company_name', 'Unknown')}
City: {supplier_data.get('city', 'India')}
Business Type: {supplier_data.get('nature_of_business', 'N/A')}
Year Established: {supplier_data.get('year_established', 'N/A')}
Certifications: {', '.join(supplier_data.get('certifications', []) or [])}
Products: {', '.join(supplier_data.get('product_names', [])[:5])}

Keep it factual and professional. No marketing language."""

        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.error(f"Description generation failed: {e}")
        return None


def normalize_product_name(name: str) -> str:
    """Basic product name normalization."""
    replacements = {
        "ss ": "Stainless Steel ",
        "ms ": "Mild Steel ",
        "gi ": "Galvanized Iron ",
        "hdpe ": "HDPE ",
        "ldpe ": "LDPE ",
        "pp ": "Polypropylene ",
        "pvc ": "PVC ",
        "frp ": "FRP ",
        "upvc ": "uPVC ",
    }
    result = name
    for abbr, full in replacements.items():
        if result.lower().startswith(abbr):
            result = full + result[len(abbr):]

    return result.strip().title()
