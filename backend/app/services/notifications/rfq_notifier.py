import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier
from app.services.notifications.email import send_rfq_notification

logger = logging.getLogger(__name__)


async def notify_supplier_of_rfq(db: AsyncSession, supplier_id, rfq_data: dict):
    """Notify a supplier about a new RFQ."""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()

    if supplier and supplier.email:
        await send_rfq_notification(supplier.email, rfq_data)
    else:
        logger.warning(f"No email for supplier {supplier_id}, RFQ notification skipped")
