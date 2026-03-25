import logging
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier

logger = logging.getLogger(__name__)


async def find_existing_supplier(
    db: AsyncSession,
    gst_number: str | None = None,
    phone: str | None = None,
    company_name: str | None = None,
) -> Supplier | None:
    """
    Find existing supplier by:
    1. GST number (strongest match)
    2. Phone + company name (fuzzy match)
    """
    # Try GST match first
    if gst_number:
        result = await db.execute(
            select(Supplier).where(Supplier.gst_number == gst_number)
        )
        supplier = result.scalar_one_or_none()
        if supplier:
            return supplier

    # Try phone + company name
    if phone and company_name:
        result = await db.execute(
            select(Supplier).where(
                or_(Supplier.phone == phone, Supplier.mobile == phone),
                Supplier.company_name == company_name,
            )
        )
        supplier = result.scalar_one_or_none()
        if supplier:
            return supplier

    return None


def deduplicate_batch(records: list[dict]) -> list[dict]:
    """Remove duplicates within a batch based on GST and phone+company."""
    seen_gst = set()
    seen_phone_company = set()
    unique = []

    for record in records:
        gst = record.get("gst_number")
        if gst and gst in seen_gst:
            continue
        if gst:
            seen_gst.add(gst)

        phone = record.get("phone") or record.get("mobile")
        company = record.get("company_name", "").lower().strip()
        key = f"{phone}:{company}"
        if phone and company and key in seen_phone_company:
            continue
        if phone and company:
            seen_phone_company.add(key)

        unique.append(record)

    logger.info(f"Dedup: {len(records)} → {len(unique)} records")
    return unique
