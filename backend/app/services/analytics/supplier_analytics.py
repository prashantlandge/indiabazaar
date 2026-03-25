import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier

logger = logging.getLogger(__name__)


async def get_top_viewed_suppliers(db: AsyncSession, limit: int = 20) -> list[dict]:
    """Get most viewed suppliers."""
    result = await db.execute(
        select(Supplier.company_name, Supplier.slug, Supplier.view_count)
        .order_by(Supplier.view_count.desc())
        .limit(limit)
    )
    return [
        {"company_name": r.company_name, "slug": r.slug, "view_count": r.view_count}
        for r in result.all()
    ]


async def get_top_inquired_suppliers(db: AsyncSession, limit: int = 20) -> list[dict]:
    """Get suppliers with most inquiries."""
    result = await db.execute(
        select(Supplier.company_name, Supplier.slug, Supplier.inquiry_count)
        .order_by(Supplier.inquiry_count.desc())
        .limit(limit)
    )
    return [
        {"company_name": r.company_name, "slug": r.slug, "inquiry_count": r.inquiry_count}
        for r in result.all()
    ]
