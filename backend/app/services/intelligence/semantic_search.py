import logging
from uuid import UUID

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.search import ParsedIntent, SearchFilters
from app.services.intelligence.embeddings import generate_embedding

logger = logging.getLogger(__name__)


async def hybrid_search(
    db: AsyncSession,
    intent: ParsedIntent,
    filters: SearchFilters,
) -> list[dict]:
    """
    Hybrid search combining:
    1. pgvector cosine similarity (semantic)
    2. PostgreSQL full-text search (tsvector)
    3. Hard filters (location, certifications, verified)

    Returns raw scored results before final ranking.
    """
    search_text = intent.expanded_query or intent.product or ""
    if not search_text.strip():
        return []

    # Generate query embedding
    query_embedding = generate_embedding(search_text)

    results = {}

    # 1. Semantic search on suppliers via pgvector
    if query_embedding:
        semantic_q = (
            select(
                Supplier,
                (1 - Supplier.embedding.cosine_distance(query_embedding)).label("semantic_score"),
            )
            .where(Supplier.embedding.isnot(None))
            .order_by(Supplier.embedding.cosine_distance(query_embedding))
            .limit(100)
        )
        semantic_results = await db.execute(semantic_q)
        for row in semantic_results.all():
            supplier = row[0]
            score = float(row[1]) if row[1] else 0
            results[supplier.id] = {
                "supplier": supplier,
                "semantic_score": score,
                "fts_score": 0,
                "product_semantic_score": 0,
                "matched_products": [],
            }

    # 2. Full-text search on suppliers
    ts_query = func.plainto_tsquery("english", search_text)
    fts_q = (
        select(
            Supplier,
            func.ts_rank(Supplier.search_vector, ts_query).label("fts_rank"),
        )
        .where(Supplier.search_vector.op("@@")(ts_query))
        .order_by(text("fts_rank DESC"))
        .limit(100)
    )
    fts_results = await db.execute(fts_q)
    for row in fts_results.all():
        supplier = row[0]
        score = float(row[1]) if row[1] else 0
        if supplier.id in results:
            results[supplier.id]["fts_score"] = score
        else:
            results[supplier.id] = {
                "supplier": supplier,
                "semantic_score": 0,
                "fts_score": score,
                "product_semantic_score": 0,
                "matched_products": [],
            }

    # 3. Product-level search
    if query_embedding:
        product_q = (
            select(
                Product,
                (1 - Product.embedding.cosine_distance(query_embedding)).label("pscore"),
            )
            .where(Product.embedding.isnot(None))
            .order_by(Product.embedding.cosine_distance(query_embedding))
            .limit(200)
        )
        product_results = await db.execute(product_q)
        for row in product_results.all():
            product = row[0]
            pscore = float(row[1]) if row[1] else 0
            sid = product.supplier_id

            if sid in results:
                results[sid]["product_semantic_score"] = max(
                    results[sid]["product_semantic_score"], pscore
                )
                results[sid]["matched_products"].append(product)
            else:
                # Need to load supplier
                supplier_result = await db.execute(
                    select(Supplier).where(Supplier.id == sid)
                )
                supplier = supplier_result.scalar_one_or_none()
                if supplier:
                    results[sid] = {
                        "supplier": supplier,
                        "semantic_score": 0,
                        "fts_score": 0,
                        "product_semantic_score": pscore,
                        "matched_products": [product],
                    }

    # Product FTS
    product_fts_q = (
        select(Product)
        .where(Product.search_vector.op("@@")(ts_query))
        .limit(200)
    )
    product_fts_results = await db.execute(product_fts_q)
    for product in product_fts_results.scalars().all():
        sid = product.supplier_id
        if sid in results:
            if product not in results[sid]["matched_products"]:
                results[sid]["matched_products"].append(product)
        else:
            supplier_result = await db.execute(
                select(Supplier).where(Supplier.id == sid)
            )
            supplier = supplier_result.scalar_one_or_none()
            if supplier:
                results[sid] = {
                    "supplier": supplier,
                    "semantic_score": 0,
                    "fts_score": 0,
                    "product_semantic_score": 0,
                    "matched_products": [product],
                }

    # 4. Apply hard filters
    filtered = {}
    for sid, data in results.items():
        supplier = data["supplier"]

        if filters.city and supplier.city and supplier.city not in filters.city:
            continue
        if filters.state and supplier.state and supplier.state not in [s for s in filters.state]:
            continue
        if filters.verified_only and not (supplier.gst_verified or supplier.indiamart_verified):
            continue
        if filters.min_trust_score and supplier.trust_score < filters.min_trust_score:
            continue
        if filters.certifications:
            supplier_certs = supplier.certifications or []
            if not any(
                c.upper() in [sc.upper() for sc in supplier_certs]
                for c in filters.certifications
            ):
                continue
        if filters.nature_of_business:
            if supplier.nature_of_business and supplier.nature_of_business not in filters.nature_of_business:
                continue

        filtered[sid] = data

    return list(filtered.values())
