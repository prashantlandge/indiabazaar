from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class RFQCreate(BaseModel):
    supplier_id: UUID | None = None
    product_name: str
    quantity: str
    unit: str | None = None
    target_price: str | None = None
    delivery_location: str | None = None
    required_by: date | None = None
    certifications_needed: list[str] | None = None
    message: str | None = None


class RFQResponse(BaseModel):
    id: UUID
    buyer_id: UUID | None
    supplier_id: UUID | None
    product_name: str
    quantity: str
    unit: str | None
    target_price: str | None
    delivery_location: str | None
    required_by: date | None
    certifications_needed: list[str] | None
    message: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RFQStatusUpdate(BaseModel):
    status: str


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None
    company_name: str | None = None
    phone: str | None = None
    city: str | None = None
    industry: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    company_name: str | None
    phone: str | None
    city: str | None
    industry: str | None
    is_verified: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
