from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.rfq import RFQ
from app.schemas.rfq import RFQCreate, RFQResponse, RFQStatusUpdate

router = APIRouter()


@router.post("", response_model=RFQResponse, status_code=201)
async def create_rfq(data: RFQCreate, db: AsyncSession = Depends(get_db)):
    rfq = RFQ(
        supplier_id=data.supplier_id,
        product_name=data.product_name,
        quantity=data.quantity,
        unit=data.unit,
        target_price=data.target_price,
        delivery_location=data.delivery_location,
        required_by=data.required_by,
        certifications_needed=data.certifications_needed,
        message=data.message,
    )
    db.add(rfq)
    await db.flush()
    await db.refresh(rfq)
    return rfq


@router.get("", response_model=list[RFQResponse])
async def list_rfqs(
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(RFQ).order_by(RFQ.created_at.desc())
    if status:
        query = query.where(RFQ.status == status)
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/{rfq_id}/status", response_model=RFQResponse)
async def update_rfq_status(
    rfq_id: UUID, data: RFQStatusUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(RFQ).where(RFQ.id == rfq_id))
    rfq = result.scalar_one_or_none()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    if data.status not in ("pending", "viewed", "replied", "closed"):
        raise HTTPException(status_code=400, detail="Invalid status")

    rfq.status = data.status
    return rfq
