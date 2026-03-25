import logging
from collections import Counter

from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.product import ProductResponse
from app.schemas.search import (
    AvailableFilters,
    FilterOption,
    ParsedIntent,
    SearchFilters,
)
from app.schemas.supplier import SupplierResponse, SupplierSearchResult
from app.services.intelligence.trust_scorer import get_trust_breakdown

logger = logging.getLogger(__name__)


async def rank_results(
    raw_results: list[dict],
    intent: ParsedIntent,
    filters: SearchFilters,
) -> tuple[list[SupplierSearchResult], AvailableFilters]:
    """
    Apply business-logic ranking on top of search scores.

    Returns ranked SupplierSearchResult objects and available filter facets.
    """
    scored = []

    for item in raw_results:
        supplier: Supplier = item["supplier"]
        semantic_score = item.get("semantic_score", 0)
        fts_score = item.get("fts_score", 0)
        product_semantic_score = item.get("product_semantic_score", 0)
        matched_products: list[Product] = item.get("matched_products", [])

        # Base score (0-100)
        base_score = (
            semantic_score * 35
            + min(fts_score * 100, 25)  # Normalize FTS score
            + product_semantic_score * 20
            + (supplier.trust_score or 0) * 0.20
        )

        # Location match bonus
        if intent.location_preference:
            loc_pref = intent.location_preference.lower()
            if supplier.city and supplier.city.lower() == loc_pref:
                base_score += 10
            elif supplier.state and supplier.state.lower() == loc_pref:
                base_score += 5

        # Certification match bonus
        if intent.certifications_required and supplier.certifications:
            supplier_certs_upper = [c.upper() for c in supplier.certifications]
            matches = sum(
                1 for c in intent.certifications_required
                if c.upper() in supplier_certs_upper
            )
            base_score += min(matches * 5, 10)

        # Boost factors
        if intent.urgency == "high":
            base_score *= 1.05

        if intent.certifications_required and supplier.certifications:
            all_match = all(
                c.upper() in [sc.upper() for sc in supplier.certifications]
                for c in intent.certifications_required
            )
            if all_match:
                base_score *= 1.15

        # Penalty factors
        if not supplier.phone and not supplier.mobile:
            base_score -= 10
        if not matched_products:
            base_score -= 5
        if (supplier.trust_score or 0) < 30:
            base_score -= 10

        # Build match reasons
        match_reasons = _build_match_reasons(supplier, intent, matched_products)
        gap_flags = _build_gap_flags(supplier, intent)

        # Trust breakdown
        supplier_dict = {
            "gst_verified": supplier.gst_verified,
            "indiamart_verified": supplier.indiamart_verified,
            "rating": supplier.rating,
            "num_reviews": supplier.num_reviews,
            "certifications": supplier.certifications,
            "trust_seal": supplier.trust_seal,
            "website": supplier.website,
            "year_established": supplier.year_established,
        }
        trust_breakdown = get_trust_breakdown(supplier_dict, len(matched_products))

        scored.append({
            "supplier": supplier,
            "final_score": max(0, min(base_score, 100)),
            "match_reasons": match_reasons,
            "gap_flags": gap_flags,
            "matched_products": matched_products[:5],
            "trust_breakdown": trust_breakdown,
        })

    # Sort by score
    scored.sort(key=lambda x: x["final_score"], reverse=True)

    # Diversity rules: max 3 from same city in top 10, max 5 same business type
    diversified = _apply_diversity(scored)

    # Build available filters from all results
    available_filters = _build_available_filters(raw_results)

    # Convert to response models
    results = []
    for item in diversified:
        supplier_resp = SupplierResponse.model_validate(item["supplier"])
        product_responses = [
            ProductResponse.model_validate(p) for p in item["matched_products"]
        ]
        results.append(SupplierSearchResult(
            supplier=supplier_resp,
            final_score=round(item["final_score"], 1),
            match_reasons=item["match_reasons"],
            gap_flags=item["gap_flags"],
            matched_products=product_responses,
            trust_breakdown=item["trust_breakdown"],
        ))

    return results, available_filters


def _build_match_reasons(
    supplier: Supplier, intent: ParsedIntent, products: list[Product]
) -> list[str]:
    reasons = []

    if intent.product and products:
        reasons.append(f"Offers products matching \"{intent.product}\"")

    if supplier.nature_of_business:
        reasons.append(f"{supplier.nature_of_business} with direct supply")

    if supplier.certifications and intent.certifications_required:
        matching = [
            c for c in supplier.certifications
            if c.upper() in [r.upper() for r in intent.certifications_required]
        ]
        if matching:
            reasons.append(f"{', '.join(matching)} certified — matches your requirement")

    if intent.location_preference and supplier.city:
        if supplier.city.lower() == intent.location_preference.lower():
            reasons.append(f"Located in {supplier.city} — your preferred location")
        elif supplier.state and supplier.state.lower() == intent.location_preference.lower():
            reasons.append(f"Located in {supplier.city}, {supplier.state}")

    if supplier.rating and supplier.num_reviews:
        reasons.append(f"{supplier.rating} star rating from {supplier.num_reviews} reviews")

    if supplier.year_established:
        from datetime import datetime, timezone
        age = datetime.now(timezone.utc).year - supplier.year_established
        if age > 5:
            reasons.append(f"Established {supplier.year_established} — {age} years in business")

    if supplier.gst_verified:
        reasons.append("GST verified supplier")

    # Ensure at least 2 reasons
    if len(reasons) < 2:
        if supplier.city:
            reasons.append(f"Based in {supplier.city}")
        if not reasons:
            reasons.append("Relevant supplier for your search")

    return reasons[:5]


def _build_gap_flags(supplier: Supplier, intent: ParsedIntent) -> list[str]:
    flags = []

    if not supplier.phone and not supplier.mobile:
        flags.append("Phone number requires verification")

    if intent.certifications_required and supplier.certifications:
        missing = [
            c for c in intent.certifications_required
            if c.upper() not in [sc.upper() for sc in (supplier.certifications or [])]
        ]
        if missing:
            flags.append(f"Missing certifications: {', '.join(missing)}")
    elif intent.certifications_required and not supplier.certifications:
        flags.append(f"Certification status unknown")

    if not supplier.gst_verified:
        flags.append("GST verification pending")

    return flags


def _apply_diversity(scored: list[dict]) -> list[dict]:
    """Ensure diversity in top results."""
    result = []
    city_counts = Counter()
    biz_counts = Counter()

    for item in scored:
        supplier = item["supplier"]
        city = supplier.city or "unknown"
        biz = supplier.nature_of_business or "unknown"

        in_top_10 = len(result) < 10
        if in_top_10:
            if city_counts[city] >= 3:
                continue
            if biz_counts[biz] >= 5:
                continue

        city_counts[city] += 1
        biz_counts[biz] += 1
        result.append(item)

    return result


def _build_available_filters(raw_results: list[dict]) -> AvailableFilters:
    cities = Counter()
    states = Counter()
    certs = Counter()
    biz_types = Counter()

    for item in raw_results:
        supplier = item["supplier"]
        if supplier.city:
            cities[supplier.city] += 1
        if supplier.state:
            states[supplier.state] += 1
        if supplier.certifications:
            for c in supplier.certifications:
                certs[c] += 1
        if supplier.nature_of_business:
            biz_types[supplier.nature_of_business] += 1

    return AvailableFilters(
        cities=[FilterOption(value=k, count=v) for k, v in cities.most_common(20)],
        states=[FilterOption(value=k, count=v) for k, v in states.most_common(20)],
        certifications=[FilterOption(value=k, count=v) for k, v in certs.most_common(20)],
        nature_of_business=[FilterOption(value=k, count=v) for k, v in biz_types.most_common(20)],
    )
