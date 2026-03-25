from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SupplierBase(BaseModel):
    company_name: str
    gst_number: str | None = None
    year_established: int | None = None
    nature_of_business: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    website: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    country: str = "India"
    indiamart_verified: bool = False
    gst_verified: bool = False
    trust_seal: bool = False
    rating: float | None = None
    num_reviews: int = 0
    annual_turnover: str | None = None
    num_employees: str | None = None
    certifications: list[str] | None = None
    source_url: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: UUID
    slug: str
    trust_score: int
    profile_completeness: int
    view_count: int
    inquiry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierSearchResult(BaseModel):
    supplier: SupplierResponse
    final_score: float
    match_reasons: list[str]
    gap_flags: list[str]
    matched_products: list["ProductResponse"]
    trust_breakdown: dict

    model_config = {"from_attributes": True}


class SupplierListResponse(BaseModel):
    suppliers: list[SupplierResponse]
    total: int
    page: int
    per_page: int


from app.schemas.product import ProductResponse  # noqa: E402

SupplierSearchResult.model_rebuild()
