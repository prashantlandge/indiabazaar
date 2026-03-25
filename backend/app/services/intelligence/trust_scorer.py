from datetime import datetime, timezone


COMPLETENESS_FIELDS = [
    "company_name", "gst_number", "contact_person", "phone",
    "address", "city", "state", "year_established",
    "nature_of_business", "annual_turnover", "num_employees",
    "certifications", "website",
]


def compute_trust_score(supplier_data: dict, product_count: int = 0) -> int:
    """Compute a 0-100 trust score for a supplier based on available signals."""
    score = 0

    # GST verified (20 pts)
    if supplier_data.get("gst_verified"):
        score += 20

    # IndiaMart verified (15 pts)
    if supplier_data.get("indiamart_verified"):
        score += 15

    # Has rating (10 pts)
    rating = supplier_data.get("rating")
    if rating is not None and rating > 0:
        score += 10

    # Rating quality (10 pts)
    if rating is not None:
        if rating >= 4.0:
            score += 10
        elif rating >= 3.5:
            score += 5

    # Number of reviews (10 pts)
    num_reviews = supplier_data.get("num_reviews", 0) or 0
    if num_reviews >= 10:
        score += 10
    elif num_reviews >= 5:
        score += 5

    # Has certifications (10 pts)
    certs = supplier_data.get("certifications")
    if certs and len(certs) > 0:
        score += 10

    # Profile completeness (10 pts)
    completeness = compute_profile_completeness(supplier_data, product_count)
    if completeness >= 80:
        score += 10
    elif completeness >= 60:
        score += 7
    elif completeness >= 40:
        score += 4

    # Established age (10 pts)
    year_est = supplier_data.get("year_established")
    if year_est:
        age = datetime.now(timezone.utc).year - year_est
        if age > 10:
            score += 10
        elif age > 5:
            score += 5

    # Trust seal (5 pts)
    if supplier_data.get("trust_seal"):
        score += 5

    # Has website (5 pts)
    if supplier_data.get("website"):
        score += 5

    # Product count (5 pts)
    if product_count >= 5:
        score += 5

    return min(score, 100)


def compute_profile_completeness(supplier_data: dict, product_count: int = 0) -> int:
    """Compute profile completeness as a percentage (0-100)."""
    total = len(COMPLETENESS_FIELDS) + 1  # +1 for products
    present = 0

    for field in COMPLETENESS_FIELDS:
        value = supplier_data.get(field)
        if value is not None and value != "" and value != []:
            present += 1

    if product_count > 0:
        present += 1

    return int((present / total) * 100)


def get_trust_breakdown(supplier_data: dict, product_count: int = 0) -> dict:
    """Return a detailed breakdown of trust score components."""
    rating = supplier_data.get("rating")
    year_est = supplier_data.get("year_established")
    age = (datetime.now(timezone.utc).year - year_est) if year_est else 0

    return {
        "gst_verified": supplier_data.get("gst_verified", False),
        "indiamart_verified": supplier_data.get("indiamart_verified", False),
        "rating": float(rating) if rating else None,
        "num_reviews": supplier_data.get("num_reviews", 0),
        "certifications": supplier_data.get("certifications", []),
        "trust_seal": supplier_data.get("trust_seal", False),
        "has_website": bool(supplier_data.get("website")),
        "year_established": year_est,
        "years_in_business": age,
        "product_count": product_count,
        "profile_completeness": compute_profile_completeness(supplier_data, product_count),
    }
