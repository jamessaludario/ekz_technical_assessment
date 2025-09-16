# repricing_pipeline/db/inspect_db.py

import sqlite3
from repricing_pipeline.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    # List tables
    print("\n--- Tables ---")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for row in cur.fetchall():
        print(row["name"])

    # Schema for each table
    print("\n--- Schema for each table ---")
    for table in ["vendors", "products"]:
        print(f"\nSchema for {table}:")
        cur.execute(f"PRAGMA table_info({table});")
        for row in cur.fetchall():
            print(tuple(row))

    # Total products
    print("\n--- Total Products ---")
    cur.execute("SELECT COUNT(*) as cnt FROM products;")
    print(cur.fetchone()["cnt"])

    # Sample products (join with vendors)
    print("\n--- Sample Products ---")
    cur.execute("""
        SELECT p.id, v.name AS vendor_name, p.sku, p.title, p.calculated_price
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        LIMIT 10;
    """)
    for row in cur.fetchall():
        print(dict(row))

    # Products per Vendor
    print("\n--- Products per Vendor ---")
    cur.execute("""
        SELECT v.name, COUNT(*) as cnt
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        GROUP BY v.name
        ORDER BY cnt DESC;
    """)
    for row in cur.fetchall():
        print(dict(row))

    # Top 5 Most Expensive Products
    print("\n--- Top 5 Most Expensive Products ---")
    cur.execute("""
        SELECT p.title, v.name AS vendor_name, p.calculated_price
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        ORDER BY p.calculated_price DESC
        LIMIT 5;
    """)
    for row in cur.fetchall():
        print(dict(row))

    conn.close()
