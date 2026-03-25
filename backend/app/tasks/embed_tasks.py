import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_supplier_embeddings")
def generate_supplier_embeddings(supplier_ids: list[str]):
    """Generate embeddings for a batch of suppliers."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    from app.core.config import get_settings
    from app.models.supplier import Supplier
    from app.models.product import Product
    from app.services.intelligence.embeddings import (
        build_supplier_text,
        build_product_text,
        generate_embedding,
        generate_embeddings_batch,
    )

    settings = get_settings()
    engine = create_engine(settings.DATABASE_SYNC_URL)

    with Session(engine) as session:
        for sid in supplier_ids:
            try:
                supplier = session.execute(
                    select(Supplier).where(Supplier.id == sid)
                ).scalar_one_or_none()
                if not supplier:
                    continue

                # Get products
                products = session.execute(
                    select(Product).where(Product.supplier_id == supplier.id)
                ).scalars().all()

                # Build supplier embedding text
                supplier_dict = {
                    "company_name": supplier.company_name,
                    "city": supplier.city,
                    "nature_of_business": supplier.nature_of_business,
                    "certifications": supplier.certifications,
                    "products": [{"name": p.name, "description": p.description} for p in products],
                }
                text = build_supplier_text(supplier_dict)
                embedding = generate_embedding(text)
                if embedding:
                    supplier.embedding = embedding

                # Build product embeddings
                for product in products:
                    product_dict = {
                        "name": product.name,
                        "description": product.description,
                        "category": product.category,
                        "subcategory": product.subcategory,
                        "specs": product.specs,
                    }
                    ptext = build_product_text(product_dict)
                    pembed = generate_embedding(ptext)
                    if pembed:
                        product.embedding = pembed

                session.commit()
                logger.info(f"Embeddings generated for supplier {sid}")

            except Exception as e:
                logger.error(f"Embedding generation failed for {sid}: {e}")
                session.rollback()

    engine.dispose()
