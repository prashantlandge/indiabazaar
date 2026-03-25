import re

from app.services.intelligence.enricher import normalize_city


def normalize_phone(phone: str | None) -> str | None:
    """Normalize phone numbers to +91XXXXXXXXXX format."""
    if not phone:
        return None
    digits = re.sub(r"[^\d]", "", phone)
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"+91{digits[1:]}"
    return phone.strip()


def normalize_price(price_str: str | None) -> dict:
    """Parse price strings like '₹500 - ₹1,000' into structured data."""
    if not price_str:
        return {"min": None, "max": None, "unit": None}

    price_str = price_str.replace("₹", "").replace(",", "").strip()

    # Extract unit
    unit = None
    unit_patterns = [
        (r"/\s*(kg|kilogram)", "per kg"),
        (r"/\s*(piece|pc|pcs)", "per piece"),
        (r"/\s*(ton|tonne|mt)", "per ton"),
        (r"/\s*(meter|mtr|m)", "per meter"),
        (r"/\s*(liter|litre|l)", "per liter"),
        (r"/\s*(set)", "per set"),
        (r"/\s*(box)", "per box"),
        (r"/\s*(pair)", "per pair"),
        (r"/\s*(unit)", "per unit"),
        (r"/\s*(sq\s*ft|sqft|square\s*feet)", "per sq ft"),
    ]
    for pattern, u in unit_patterns:
        if re.search(pattern, price_str, re.IGNORECASE):
            unit = u
            price_str = re.sub(pattern, "", price_str, flags=re.IGNORECASE)
            break

    # Extract numbers
    numbers = re.findall(r"[\d.]+", price_str)
    numbers = [float(n) for n in numbers if n]

    if len(numbers) >= 2:
        return {"min": min(numbers), "max": max(numbers), "unit": unit}
    elif len(numbers) == 1:
        return {"min": numbers[0], "max": numbers[0], "unit": unit}

    return {"min": None, "max": None, "unit": unit}


def normalize_supplier_data(raw: dict) -> dict:
    """Normalize a raw supplier record from scraper output."""
    normalized = {**raw}

    # Normalize phone numbers
    if "phone" in normalized:
        normalized["phone"] = normalize_phone(normalized.get("phone"))
    if "mobile" in normalized:
        normalized["mobile"] = normalize_phone(normalized.get("mobile"))

    # Normalize city
    if "city" in normalized:
        normalized["city"] = normalize_city(normalized.get("city"))

    # Normalize state
    state = normalized.get("state", "")
    if state:
        normalized["state"] = state.strip().title()

    # Normalize company name
    company = normalized.get("company_name", "")
    if company:
        normalized["company_name"] = company.strip()

    # Normalize certifications
    certs = normalized.get("certifications")
    if isinstance(certs, str):
        normalized["certifications"] = [c.strip() for c in certs.split(",") if c.strip()]
    elif not isinstance(certs, list):
        normalized["certifications"] = []

    # Normalize boolean fields
    for field in ["indiamart_verified", "gst_verified", "trust_seal"]:
        val = normalized.get(field)
        if isinstance(val, str):
            normalized[field] = val.lower() in ("true", "yes", "1", "verified")

    # Normalize year
    year = normalized.get("year_established")
    if isinstance(year, str):
        nums = re.findall(r"\d{4}", year)
        normalized["year_established"] = int(nums[0]) if nums else None

    # Normalize rating
    rating = normalized.get("rating")
    if isinstance(rating, str):
        nums = re.findall(r"[\d.]+", rating)
        normalized["rating"] = float(nums[0]) if nums else None

    return normalized
