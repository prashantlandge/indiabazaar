import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Index, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    gst_number: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    year_established: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nature_of_business: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    mobile: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(Text, nullable=True)
    pincode: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(Text, default="India")
    member_since: Mapped[str | None] = mapped_column(Text, nullable=True)
    indiamart_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    gst_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    trust_seal: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    num_reviews: Mapped[int] = mapped_column(Integer, default=0)
    annual_turnover: Mapped[str | None] = mapped_column(Text, nullable=True)
    num_employees: Mapped[str | None] = mapped_column(Text, nullable=True)
    certifications: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    trust_score: Mapped[int] = mapped_column(Integer, default=0)
    profile_completeness: Mapped[int] = mapped_column(Integer, default=0)
    embedding = mapped_column(Vector(384), nullable=True)
    search_vector = mapped_column(TSVECTOR, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    inquiry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    products: Mapped[list["Product"]] = relationship(back_populates="supplier", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_suppliers_search_vector", "search_vector", postgresql_using="gin"),
        Index("idx_suppliers_city_state", "city", "state"),
        Index("idx_suppliers_trust_score", trust_score.desc()),
    )


from app.models.product import Product  # noqa: E402
