# repricing_pipeline/load.py

import sqlite3
from typing import List, Dict
import os
from pathlib import Path
from .config import DB_PATH, SCHEMA_PATH


def _get_connection(db_path: Path = None):
    """Return a SQLite connection with foreign keys enabled."""
    db_path = db_path or DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = None):
    """Initializes a fresh database, deleting old one if it exists."""
    db_path = db_path or DB_PATH
    Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Old database removed: {db_path}")

    conn = _get_connection(db_path)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialized: {db_path}")


def upsert_products(products: List[Dict], db_path: Path = None):
    conn = _get_connection(db_path)

    # --- Prepare vendors ---
    vendors = {
        p["vendor_id"]: {
            "vendor_id": p["vendor_id"],
            "name": p.get("vendor_name") or "Unknown Vendor"
        }
        for p in products
    }
    _upsert_lookup_table(conn, "vendors", list(vendors.values()), key_field="vendor_id")

    # --- Prepare brands ---
    brands = {
        p["brand_id"]: {
            "brand_id": p["brand_id"],
            "name": p.get("brand_name") or "Unknown Brand",
            "vendor_id": p.get("vendor_id")
        }
        for p in products if p.get("brand_id") is not None
    }
    _upsert_lookup_table(conn, "brands", list(brands.values()), key_field="brand_id", extra_fields=["vendor_id"])

    # --- Prepare categories ---
    categories = {
        p["category_id"]: {
            "category_id": p["category_id"],
            "name": p.get("category_name") or "Unknown Category",
            "vendor_id": p.get("vendor_id")
        }
        for p in products if p.get("category_id") is not None
    }
    _upsert_lookup_table(conn, "categories", list(categories.values()), key_field="category_id", extra_fields=["vendor_id"])

    # --- Prepare shipping tiers ---
    shipping_tiers = {
        p["shipping_tier_id"]: {
            "shipping_tier_id": p["shipping_tier_id"],
            "shipping_tier": p.get("shipping_tier") or "Standard",
            "shipping_cost": p.get("shipping_cost") or 0.0,
            "vendor_id": p.get("vendor_id")
        }
        for p in products if p.get("shipping_tier_id") is not None
    }
    _upsert_lookup_table(
        conn,
        "shipping_tiers",
        list(shipping_tiers.values()),
        key_field="shipping_tier_id",
        extra_fields=["shipping_tier", "shipping_cost", "vendor_id"]
    )

    # --- Upsert products ---
    with conn:
        cur = conn.cursor()
        for p in products:
            try:
                cur.execute(
                    """
                    INSERT INTO products (id, vendor_id, sku, name, brand_id, category_id, cost, shipping_cost, shipping_tier_id, extra_cost_applied, target_margin, calculated_price, calculated_raw_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        calculated_price=excluded.calculated_price,
                        calculated_raw_price=excluded.calculated_raw_price,
                        cost=excluded.cost,
                        shipping_cost=excluded.shipping_cost
                    """,
                    (
                        p.get("id"),
                        p.get("vendor_id"),
                        p.get("sku"),
                        p.get("name"),
                        p.get("brand_id"),
                        p.get("category_id"),
                        p.get("cost"),
                        p.get("shipping_cost"),
                        p.get("shipping_tier_id"),
                        p.get("extra_cost_applied"),
                        p.get("target_margin"),
                        p.get("calculated_price"),
                        p.get("calculated_raw_price"),
                    ),
                )
            except sqlite3.IntegrityError:
                # Skip invalid foreign keys
                continue


def _upsert_lookup_table(conn, table_name: str, rows: List[Dict], key_field: str, extra_fields: List[str] = None):
    """Generic UPSERT for lookup tables (vendors, brands, categories, shipping tiers)."""
    extra_fields = extra_fields or []

    name_field_map = {
        "vendors": "name",
        "brands": "name",
        "categories": "name",
        "shipping_tiers": "shipping_tier",
    }
    name_field = name_field_map.get(table_name)

    all_fields = [key_field] + ([name_field] if name_field else []) + extra_fields

    with conn:
        cur = conn.cursor()
        for row in rows:
            values = [row.get(f) for f in all_fields]
            placeholders = ", ".join("?" for _ in all_fields)
            update_set = ", ".join(f"{f}=excluded.{f}" for f in all_fields if f != key_field)

            cur.execute(
                f"""
                INSERT INTO {table_name} ({', '.join(all_fields)})
                VALUES ({placeholders})
                ON CONFLICT({key_field}) DO UPDATE SET {update_set}
                """,
                tuple(values)
            )
