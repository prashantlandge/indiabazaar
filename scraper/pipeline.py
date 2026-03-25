#!/usr/bin/env python3
"""
Pipeline: Orchestrates scrape → normalize → enrich → embed → store

CLI usage:
  python pipeline.py --input indiamart_suppliers.json --query "packaging material"
  python pipeline.py --input indiamart_suppliers.csv --dry-run
"""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.ingestion.importer import import_data
from app.core.database import async_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def run_pipeline(input_path: str, dry_run: bool = False):
    """Run the full ingestion pipeline."""
    path = Path(input_path)
    if not path.exists():
        logger.error(f"File not found: {input_path}")
        return

    ext = path.suffix.lstrip(".").lower()
    if ext not in ("json", "csv"):
        logger.error(f"Unsupported file type: {ext}")
        return

    content = path.read_bytes()
    logger.info(f"Read {len(content)} bytes from {input_path}")

    if dry_run:
        # Parse and validate only
        from app.services.ingestion.importer import _parse_file
        from app.services.ingestion.normalizer import normalize_supplier_data
        from app.services.ingestion.deduplicator import deduplicate_batch

        records = _parse_file(content, ext)
        logger.info(f"Parsed {len(records)} records")

        normalized = [normalize_supplier_data(r) for r in records]
        unique = deduplicate_batch(normalized)
        logger.info(f"After dedup: {len(unique)} unique records")

        for i, rec in enumerate(unique[:3]):
            logger.info(f"Sample {i+1}: {rec.get('company_name')} | {rec.get('city')} | {rec.get('gst_number')}")
        return

    async with async_session() as db:
        result = await import_data(content, ext, db, "cli-pipeline")
        await db.commit()

    logger.info(f"Pipeline complete: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TradeRadar data ingestion pipeline")
    parser.add_argument("--input", "-i", required=True, help="Input JSON or CSV file path")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without importing")
    parser.add_argument("--query", "-q", help="Original search query (for metadata)")
    args = parser.parse_args()

    asyncio.run(run_pipeline(args.input, args.dry_run))
