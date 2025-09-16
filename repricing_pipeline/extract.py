# repricing_pipeline/extract.py

import logging
from .api_client import fetch_all_products

logger = logging.getLogger(__name__)


def extract_products() -> list[dict]:
    """
    Extract products from the local API for all vendors.
    """
    logger.info("Starting extraction from API")
    products = fetch_all_products()
    logger.info(f"Extracted {len(products)} products")
    return products
