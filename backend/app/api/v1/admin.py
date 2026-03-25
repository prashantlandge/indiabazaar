import json
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product
from app.models.search_log import SearchLog
from app.models.supplier import Supplier
from app.services.ingestion.importer import import_data

router = APIRouter()


@router.post("/ingest")
async def ingest_data(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("json", "csv"):
        raise HTTPException(status_code=400, detail="Only JSON and CSV files are supported")

    content = await file.read()
    job_id = str(uuid4())

    result = await import_data(content, ext, db, job_id)
    return {
        "job_id": job_id,
        "status": "completed",
        **result,
    }


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    supplier_count = (await db.execute(select(func.count(Supplier.id)))).scalar() or 0
    product_count = (await db.execute(select(func.count(Product.id)))).scalar() or 0
    search_count = (await db.execute(select(func.count(SearchLog.id)))).scalar() or 0

    cities = (
        await db.execute(
            select(func.count(func.distinct(Supplier.city))).where(Supplier.city.isnot(None))
        )
    ).scalar() or 0

    top_searches = await db.execute(
        select(SearchLog.raw_query, func.count(SearchLog.id).label("count"))
        .where(SearchLog.raw_query != "click_track")
        .group_by(SearchLog.raw_query)
        .order_by(text("count DESC"))
        .limit(20)
    )

    return {
        "total_suppliers": supplier_count,
        "total_products": product_count,
        "total_searches": search_count,
        "cities_covered": cities,
        "top_searches": [
            {"query": row.raw_query, "count": row.count} for row in top_searches.all()
        ],
    }


@router.get("/analytics/searches")
async def search_analytics(db: AsyncSession = Depends(get_db)):
    # Top queries
    top_queries = await db.execute(
        select(SearchLog.raw_query, func.count(SearchLog.id).label("count"))
        .where(SearchLog.raw_query != "click_track")
        .group_by(SearchLog.raw_query)
        .order_by(text("count DESC"))
        .limit(20)
    )

    # Zero-result queries
    zero_results = await db.execute(
        select(SearchLog.raw_query, func.count(SearchLog.id).label("count"))
        .where(SearchLog.result_count == 0)
        .group_by(SearchLog.raw_query)
        .order_by(text("count DESC"))
        .limit(20)
    )

    # Daily volume (last 30 days)
    daily = await db.execute(
        text("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM search_logs
            WHERE created_at > NOW() - INTERVAL '30 days'
            AND raw_query != 'click_track'
            GROUP BY DATE(created_at)
            ORDER BY day
        """)
    )

    return {
        "top_queries": [{"query": r.raw_query, "count": r.count} for r in top_queries.all()],
        "zero_result_queries": [{"query": r.raw_query, "count": r.count} for r in zero_results.all()],
        "daily_volume": [{"date": str(r.day), "count": r.count} for r in daily.all()],
    }
