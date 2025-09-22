import requests
import sqlite3
from .config import API_URL, API_KEY, DB_PATH


def _get_headers():
    return {"x-api-key": API_KEY}


# ----------------- Vendors ----------------- #

def get_vendors_from_db() -> list[dict]:
    """Fetch vendors from the local DB (single source of truth)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    vendors = cur.execute("SELECT vendor_id, name FROM vendors ORDER BY vendor_id").fetchall()
    conn.close()
    return [dict(v) for v in vendors]


# ----------------- Products ----------------- #

def fetch_all_products(vendor_id: int) -> list[dict]:
    """Fetch products for a given vendor_id from the API."""
    url = f"{API_URL}/products/"
    params = {"vendor_id": vendor_id}
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json().get("data", [])


# ----------------- Categories ----------------- #

def fetch_categories(vendor_id: int) -> dict:
    """Fetch categories for a given vendor_id."""
    url = f"{API_URL}/categories/"
    params = {"vendor_id": vendor_id}
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json()


# ----------------- Brands ----------------- #

def fetch_brands(vendor_id: int) -> dict:
    """Fetch brands for a given vendor_id."""
    url = f"{API_URL}/brands/"
    params = {"vendor_id": vendor_id}
    response = requests.get(url, headers=_get_headers(), params=params)
    response.raise_for_status()
    return response.json()


# ----------------- Shipping Tiers ----------------- #

def fetch_shipping_tiers(vendor_id: int) -> dict:
    """Fetch shipping tiers for a given vendor_id."""
    url = f"{API_URL}/vendors/{vendor_id}/shipping-tiers"
    response = requests.get(url, headers=_get_headers())
    response.raise_for_status()
    return response.json()
