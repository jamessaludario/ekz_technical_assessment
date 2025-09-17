import sqlite3
import requests
from .config import API_URL, API_KEY, DB_PATH


def get_vendors_from_db() -> list[dict]:
    """Fetch vendors from the database (single source of truth)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    vendors = cur.execute("SELECT id, name FROM vendors ORDER BY id").fetchall()
    conn.close()
    return [dict(v) for v in vendors]


def fetch_products_for_vendor(vendor_id: int) -> list[dict]:
    """Fetch products for a given vendor_id from the API."""
    url = f"{API_URL}/products/"
    headers = {"x-api-key": API_KEY}
    params = {"vendor_id": vendor_id}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    payload = response.json()
    return payload.get("data", [])


def fetch_all_products() -> list[dict]:
    """Fetch products for all vendors in the DB."""
    all_products = []
    vendors = get_vendors_from_db()

    for vendor in vendors:
        try:
            products = fetch_products_for_vendor(vendor["id"])
            print(f"Fetched {len(products)} products for {vendor['name']}")
            all_products.extend(products)
        except requests.HTTPError as e:
            print(f"Warning: failed to fetch vendor {vendor['name']}: {e}")

    return all_products
