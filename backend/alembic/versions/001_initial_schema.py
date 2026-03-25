"""Initial schema with all tables

Revision ID: 001
Revises:
Create Date: 2026-03-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Suppliers table
    op.create_table(
        "suppliers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("gst_number", sa.Text(), unique=True, nullable=True),
        sa.Column("year_established", sa.Integer(), nullable=True),
        sa.Column("nature_of_business", sa.Text(), nullable=True),
        sa.Column("contact_person", sa.Text(), nullable=True),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("mobile", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("state", sa.Text(), nullable=True),
        sa.Column("pincode", sa.Text(), nullable=True),
        sa.Column("country", sa.Text(), server_default="India"),
        sa.Column("member_since", sa.Text(), nullable=True),
        sa.Column("indiamart_verified", sa.Boolean(), server_default="false"),
        sa.Column("gst_verified", sa.Boolean(), server_default="false"),
        sa.Column("trust_seal", sa.Boolean(), server_default="false"),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("num_reviews", sa.Integer(), server_default="0"),
        sa.Column("annual_turnover", sa.Text(), nullable=True),
        sa.Column("num_employees", sa.Text(), nullable=True),
        sa.Column("certifications", ARRAY(sa.Text()), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("trust_score", sa.Integer(), server_default="0"),
        sa.Column("profile_completeness", sa.Integer(), server_default="0"),
        sa.Column("view_count", sa.Integer(), server_default="0"),
        sa.Column("inquiry_count", sa.Integer(), server_default="0"),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    # Add vector column separately (alembic doesn't natively handle it)
    op.execute("ALTER TABLE suppliers ADD COLUMN embedding vector(384)")
    op.execute("ALTER TABLE suppliers ADD COLUMN search_vector tsvector")

    # Products table
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("supplier_id", UUID(as_uuid=True), sa.ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("subcategory", sa.Text(), nullable=True),
        sa.Column("price_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_unit", sa.Text(), nullable=True),
        sa.Column("min_order_qty", sa.Text(), nullable=True),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("specs", JSONB(), server_default="{}"),
        sa.Column("view_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.execute("ALTER TABLE products ADD COLUMN embedding vector(384)")
    op.execute("ALTER TABLE products ADD COLUMN search_vector tsvector")

    # Users table
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text(), unique=True, nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=True),
        sa.Column("company_name", sa.Text(), nullable=True),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("industry", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default="false"),
        sa.Column("is_admin", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # RFQs table
    op.create_table(
        "rfqs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("buyer_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("supplier_id", UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=True),
        sa.Column("product_name", sa.Text(), nullable=False),
        sa.Column("quantity", sa.Text(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("target_price", sa.Text(), nullable=True),
        sa.Column("delivery_location", sa.Text(), nullable=True),
        sa.Column("required_by", sa.Date(), nullable=True),
        sa.Column("certifications_needed", ARRAY(sa.Text()), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # Saved suppliers table
    op.create_table(
        "saved_suppliers",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("supplier_id", UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), primary_key=True),
        sa.Column("saved_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # Search logs table
    op.create_table(
        "search_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("raw_query", sa.Text(), nullable=False),
        sa.Column("parsed_intent", JSONB(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("clicked_supplier_id", UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # Indexes
    op.execute(
        "CREATE INDEX idx_suppliers_embedding ON suppliers USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.execute(
        "CREATE INDEX idx_products_embedding ON products USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )
    op.create_index("idx_suppliers_search_vector", "suppliers", ["search_vector"], postgresql_using="gin")
    op.create_index("idx_products_search_vector", "products", ["search_vector"], postgresql_using="gin")
    op.create_index("idx_suppliers_city_state", "suppliers", ["city", "state"])
    op.create_index("idx_suppliers_trust_score", "suppliers", [sa.text("trust_score DESC")])
    op.create_index("idx_products_supplier", "products", ["supplier_id"])

    # Create tsvector trigger for suppliers
    op.execute("""
        CREATE OR REPLACE FUNCTION suppliers_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.company_name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.nature_of_business, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.city, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(NEW.state, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(array_to_string(NEW.certifications, ' '), '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER suppliers_search_vector_trigger
        BEFORE INSERT OR UPDATE ON suppliers
        FOR EACH ROW EXECUTE FUNCTION suppliers_search_vector_update();
    """)

    # Create tsvector trigger for products
    op.execute("""
        CREATE OR REPLACE FUNCTION products_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(NEW.category, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(NEW.subcategory, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER products_search_vector_trigger
        BEFORE INSERT OR UPDATE ON products
        FOR EACH ROW EXECUTE FUNCTION products_search_vector_update();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS products_search_vector_trigger ON products")
    op.execute("DROP FUNCTION IF EXISTS products_search_vector_update()")
    op.execute("DROP TRIGGER IF EXISTS suppliers_search_vector_trigger ON suppliers")
    op.execute("DROP FUNCTION IF EXISTS suppliers_search_vector_update()")
    op.drop_table("search_logs")
    op.drop_table("saved_suppliers")
    op.drop_table("rfqs")
    op.drop_table("users")
    op.drop_table("products")
    op.drop_table("suppliers")
