import csv
import io
import json
import logging
from datetime import datetime, timezone

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.supplier import Supplier
from app.services.ingestion.deduplicator import deduplicate_batch, find_existing_supplier
from app.services.ingestion.normalizer import normalize_price, normalize_supplier_data
from app.services.intelligence.trust_scorer import compute_profile_completeness, compute_trust_score

logger = logging.getLogger(__name__)


async def import_data(
    content: bytes, file_type: str, db: AsyncSession, job_id: str
) -> dict:
    """Import supplier data from JSON or CSV content."""
    records = _parse_file(content, file_type)
    if not records:
        return {"total": 0, "added": 0, "updated": 0, "skipped": 0, "errors": 0}

    # Normalize
    normalized = [normalize_supplier_data(r) for r in records]

    # Deduplicate within batch
    unique = deduplicate_batch(normalized)

    stats = {"total": len(records), "added": 0, "updated": 0, "skipped": 0, "errors": 0}

    for record in unique:
        try:
            await _upsert_supplier(record, db)
            stats["added"] += 1
        except Exception as e:
            logger.error(f"Import error for {record.get('company_name', 'unknown')}: {e}")
            stats["errors"] += 1

    await db.flush()
    return stats


def _parse_file(content: bytes, file_type: str) -> list[dict]:
    """Parse uploaded file into list of dicts."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    if file_type == "json":
        data = json.loads(text)
        if isinstance(data, dict):
            # Handle {"suppliers": [...]} or {"data": [...]}
            for key in ("suppliers", "data", "results", "items"):
                if key in data:
                    return data[key]
            return [data]
        return data

    if file_type == "csv":
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)

    return []


async def _upsert_supplier(record: dict, db: AsyncSession):
    """Insert or update a supplier record."""
    company_name = record.get("company_name", "").strip()
    if not company_name:
        return

    # Check for existing
    existing = await find_existing_supplier(
        db,
        gst_number=record.get("gst_number"),
        phone=record.get("phone"),
        company_name=company_name,
    )

    if existing:
        # Update existing supplier
        for key, value in record.items():
            if key in ("id", "created_at", "products"):
                continue
            if value is not None and hasattr(existing, key):
                setattr(existing, key, value)
        existing.last_scraped_at = datetime.now(timezone.utc)
        existing.updated_at = datetime.now(timezone.utc)

        # Recompute scores
        supplier_dict = _supplier_to_dict(existing)
        existing.trust_score = compute_trust_score(supplier_dict)
        existing.profile_completeness = compute_profile_completeness(supplier_dict)

        # Update products if provided
        products = record.get("products", [])
        if products:
            await _import_products(products, existing.id, db)
    else:
        # Create new supplier
        base_slug = slugify(company_name)
        slug = base_slug
        counter = 1
        from sqlalchemy import select as sa_select
        while True:
            result = await db.execute(
                sa_select(Supplier.id).where(Supplier.slug == slug)
            )
            if not result.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        supplier = Supplier(
            company_name=company_name,
            slug=slug,
            gst_number=record.get("gst_number"),
            year_established=record.get("year_established"),
            nature_of_business=record.get("nature_of_business"),
            contact_person=record.get("contact_person"),
            phone=record.get("phone"),
            mobile=record.get("mobile"),
            email=record.get("email"),
            website=record.get("website"),
            address=record.get("address"),
            city=record.get("city"),
            state=record.get("state"),
            pincode=record.get("pincode"),
            country=record.get("country", "India"),
            member_since=record.get("member_since"),
            indiamart_verified=record.get("indiamart_verified", False),
            gst_verified=record.get("gst_verified", False),
            trust_seal=record.get("trust_seal", False),
            rating=record.get("rating"),
            num_reviews=record.get("num_reviews", 0),
            annual_turnover=record.get("annual_turnover"),
            num_employees=record.get("num_employees"),
            certifications=record.get("certifications", []),
            source_url=record.get("source_url"),
            last_scraped_at=datetime.now(timezone.utc),
        )

        supplier_dict = _supplier_to_dict(supplier)
        supplier.trust_score = compute_trust_score(supplier_dict)
        supplier.profile_completeness = compute_profile_completeness(supplier_dict)

        db.add(supplier)
        await db.flush()

        # Import products
        products = record.get("products", [])
        if products:
            await _import_products(products, supplier.id, db)


async def _import_products(products: list[dict], supplier_id, db: AsyncSession):
    """Import products for a supplier."""
    for prod in products:
        name = prod.get("name", "").strip()
        if not name:
            continue

        price = normalize_price(prod.get("price"))

        product = Product(
            supplier_id=supplier_id,
            name=name,
            slug=slugify(name),
            description=prod.get("description"),
            category=prod.get("category"),
            subcategory=prod.get("subcategory"),
            price_min=price["min"],
            price_max=price["max"],
            price_unit=price["unit"],
            min_order_qty=prod.get("min_order_qty"),
            product_url=prod.get("product_url"),
            image_url=prod.get("image_url"),
            specs=prod.get("specs", {}),
        )
        db.add(product)


def _supplier_to_dict(supplier) -> dict:
    """Convert supplier model to dict for scoring."""
    return {
        "company_name": supplier.company_name,
        "gst_number": supplier.gst_number,
        "contact_person": supplier.contact_person,
        "phone": supplier.phone,
        "address": supplier.address,
        "city": supplier.city,
        "state": supplier.state,
        "year_established": supplier.year_established,
        "nature_of_business": supplier.nature_of_business,
        "annual_turnover": supplier.annual_turnover,
        "num_employees": supplier.num_employees,
        "certifications": supplier.certifications,
        "website": supplier.website,
        "gst_verified": supplier.gst_verified,
        "indiamart_verified": supplier.indiamart_verified,
        "trust_seal": supplier.trust_seal,
        "rating": supplier.rating,
        "num_reviews": supplier.num_reviews,
    }
