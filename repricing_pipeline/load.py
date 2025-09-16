# repricing_pipeline/load.py

import sqlite3
from typing import List, Dict
import os
from .config import DB_PATH
from pathlib import Path

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "db", "schema.sql")


def _get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH, seed_vendors: List[str] = None):
    Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
    conn = _get_connection(db_path)

    # Create schema
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    # Optionally seed vendors
    if seed_vendors:
        cur = conn.cursor()
        for vendor in seed_vendors:
            cur.execute(
                "INSERT OR IGNORE INTO vendors (name) VALUES (?)",
                (vendor,),
            )

    conn.commit()
    conn.close()


def upsert_products(products: List[Dict], db_path=DB_PATH):
    conn = _get_connection(db_path)
    cur = conn.cursor()

    # Cache vendors
    vendor_cache = {}
    for p in products:
        vendor = p.get("vendor") or "UNKNOWN"
        if vendor in vendor_cache:
            continue
        cur.execute("SELECT id FROM vendors WHERE name = ?", (vendor,))
        row = cur.fetchone()
        if row:
            vendor_cache[vendor] = row["id"]
        else:
            cur.execute("INSERT INTO vendors(name) VALUES(?)", (vendor,))
            vendor_cache[vendor] = cur.lastrowid

    # Upsert products
    for p in products:
        vendor_id = vendor_cache.get(p.get("vendor") or "UNKNOWN")
        product_id = p.get("id")
        if product_id is None:
            continue

        cur.execute(
            """
            UPDATE products
            SET vendor_id = ?, sku = ?, title = ?, brand = ?, category = ?,
                cost = ?, shipping_cost = ?, shipping_tier_cost = ?,
                extra_cost_applied = ?, target_margin = ?, calculated_price = ?, calculated_raw_price = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                vendor_id,
                p.get("sku"),
                p.get("title"),
                p.get("brand"),
                p.get("category"),
                p.get("cost"),
                p.get("shipping_cost"),
                p.get("shipping_tier_cost"),
                p.get("extra_cost_applied"),
                p.get("target_margin"),
                p.get("calculated_price"),
                p.get("calculated_raw_price"),
                product_id,
            ),
        )

        if cur.rowcount == 0:
            cur.execute(
                """
                INSERT INTO products (id, vendor_id, sku, title, brand, category,
                    cost, shipping_cost, shipping_tier_cost, extra_cost_applied,
                    target_margin, calculated_price, calculated_raw_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    vendor_id,
                    p.get("sku"),
                    p.get("title"),
                    p.get("brand"),
                    p.get("category"),
                    p.get("cost"),
                    p.get("shipping_cost"),
                    p.get("shipping_tier_cost"),
                    p.get("extra_cost_applied"),
                    p.get("target_margin"),
                    p.get("calculated_price"),
                    p.get("calculated_raw_price"),
                ),
            )

    conn.commit()
    conn.close()
