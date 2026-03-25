from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    price_unit: str | None = None
    min_order_qty: str | None = None
    product_url: str | None = None
    image_url: str | None = None
    specs: dict = {}


class ProductCreate(ProductBase):
    supplier_id: UUID


class ProductResponse(ProductBase):
    id: UUID
    supplier_id: UUID
    slug: str
    view_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
