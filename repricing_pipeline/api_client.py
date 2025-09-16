# repricing_pipeline/api_client.py

import requests
from .config import API_URL, API_KEY, VENDORS  # import VENDORS from config

def fetch_products_for_vendor(vendor_name: str) -> list[dict]:
    """
    Fetch products for a specific vendor using its vendor_id.
    """
    vendor_id = VENDORS.get(vendor_name)
    if vendor_id is None:
        raise ValueError(f"Unknown vendor: {vendor_name}")

    url = f"{API_URL}/products/"
    headers = {"x-api-key": API_KEY}
    params = {"vendor_id": vendor_id}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    payload = response.json()
    return payload.get("data", [])

def fetch_all_products() -> list[dict]:
    """
    Fetch products for all configured vendors.
    """
    all_products = []
    for vendor_name in VENDORS:
        try:
            products = fetch_products_for_vendor(vendor_name)
            print(f"Fetched {len(products)} products for {vendor_name}")
            all_products.extend(products)
        except requests.HTTPError as e:
            print(f"Warning: failed to fetch vendor {vendor_name}: {e}")
    return all_products
