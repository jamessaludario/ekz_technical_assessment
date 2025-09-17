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

def init_db(db_path=DB_PATH):
    Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
    conn = _get_connection(db_path)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def upsert_products(products: List[Dict], db_path=DB_PATH):
    conn = _get_connection(db_path)
    cur = conn.cursor()

    for p in products:
        vendor_id = p.get("vendor_id")
        product_id = p.get("id")

        if vendor_id is None:
            raise ValueError(f"Product missing vendor_id: {p}")
        if product_id is None:
            # skip items without ID
            continue

        # Try update first
        cur.execute("""
            UPDATE products
            SET vendor_id = ?, sku = ?, title = ?, brand = ?, category = ?,
                cost = ?, shipping_cost = ?, shipping_tier_cost = ?,
                extra_cost_applied = ?, target_margin = ?, calculated_price = ?, 
                calculated_raw_price = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
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
            product_id
        ))

        if cur.rowcount == 0:
            # Insert if not exists
            cur.execute("""
                INSERT INTO products (
                    id, vendor_id, sku, title, brand, category,
                    cost, shipping_cost, shipping_tier_cost, extra_cost_applied,
                    target_margin, calculated_price, calculated_raw_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            ))

    conn.commit()
    conn.close()
