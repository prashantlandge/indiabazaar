from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.product import ProductResponse
from app.schemas.supplier import SupplierListResponse, SupplierResponse

router = APIRouter()


@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    city: str | None = None,
    state: str | None = None,
    verified_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    query = select(Supplier)

    if city:
        query = query.where(Supplier.city == city)
    if state:
        query = query.where(Supplier.state == state)
    if verified_only:
        query = query.where(
            (Supplier.gst_verified == True) | (Supplier.indiamart_verified == True)
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    query = query.order_by(Supplier.trust_score.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    suppliers = result.scalars().all()

    return SupplierListResponse(
        suppliers=[SupplierResponse.model_validate(s) for s in suppliers],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{slug}", response_model=SupplierResponse)
async def get_supplier(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.slug == slug))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.get("/{slug}/products", response_model=list[ProductResponse])
async def get_supplier_products(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.slug == slug))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    products_result = await db.execute(
        select(Product).where(Product.supplier_id == supplier.id)
    )
    return products_result.scalars().all()


@router.get("/{slug}/similar", response_model=list[SupplierResponse])
async def get_similar_suppliers(slug: str, limit: int = 5, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.slug == slug))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    if supplier.embedding is not None:
        similar_q = (
            select(Supplier)
            .where(Supplier.id != supplier.id)
            .where(Supplier.embedding.isnot(None))
            .order_by(Supplier.embedding.cosine_distance(supplier.embedding))
            .limit(limit)
        )
        similar_result = await db.execute(similar_q)
        return similar_result.scalars().all()

    # Fallback: same city/state
    fallback_q = (
        select(Supplier)
        .where(Supplier.id != supplier.id)
        .where(Supplier.city == supplier.city)
        .order_by(Supplier.trust_score.desc())
        .limit(limit)
    )
    fallback_result = await db.execute(fallback_q)
    return fallback_result.scalars().all()


@router.post("/{slug}/view")
async def track_view(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.slug == slug))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier.view_count += 1
    return {"status": "tracked"}
