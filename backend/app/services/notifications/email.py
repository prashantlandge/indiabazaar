import logging

logger = logging.getLogger(__name__)


async def send_rfq_notification(supplier_email: str, rfq_data: dict):
    """Send RFQ notification email to supplier. Placeholder implementation."""
    logger.info(f"RFQ notification would be sent to {supplier_email}: {rfq_data}")
    # TODO: Integrate with email service (SendGrid, SES, etc.)
