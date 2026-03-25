#!/usr/bin/env python3
"""
Generate embeddings for all suppliers and products in the database.

Usage:
    python generate_embeddings.py
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import select, func
from app.core.database import async_session
from app.models.supplier import Supplier
from app.models.product import Product
from app.services.intelligence.embeddings import (
    build_supplier_text,
    build_product_text,
    generate_embedding,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def generate_all_embeddings():
    """Generate embeddings for all suppliers and products."""
    async with async_session() as db:
        # Count
        total_suppliers = (await db.execute(select(func.count(Supplier.id)))).scalar()
        total_products = (await db.execute(select(func.count(Product.id)))).scalar()
        logger.info(f"Found {total_suppliers} suppliers and {total_products} products")

        # Process suppliers in batches
        offset = 0
        batch_size = 50
        embedded_suppliers = 0

        while offset < total_suppliers:
            result = await db.execute(
                select(Supplier).offset(offset).limit(batch_size)
            )
            suppliers = result.scalars().all()
            if not suppliers:
                break

            for supplier in suppliers:
                # Get products for this supplier
                prod_result = await db.execute(
                    select(Product).where(Product.supplier_id == supplier.id)
                )
                products = prod_result.scalars().all()

                # Build supplier embedding text
                supplier_dict = {
                    "company_name": supplier.company_name,
                    "city": supplier.city,
                    "nature_of_business": supplier.nature_of_business,
                    "certifications": supplier.certifications,
                    "products": [
                        {"name": p.name, "description": p.description}
                        for p in products
                    ],
                }
                text = build_supplier_text(supplier_dict)
                embedding = generate_embedding(text)
                if embedding:
                    supplier.embedding = embedding
                    embedded_suppliers += 1

                # Generate product embeddings
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

            await db.commit()
            offset += batch_size
            logger.info(f"Processed {min(offset, total_suppliers)}/{total_suppliers} suppliers")

        logger.info(f"Embedding generation complete: {embedded_suppliers} suppliers embedded")


if __name__ == "__main__":
    asyncio.run(generate_all_embeddings())
