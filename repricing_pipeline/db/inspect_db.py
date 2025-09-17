import sqlite3
from repricing_pipeline.config import DB_PATH
from pprint import pprint

def inspect_db():
    print(f"DB_PATH = {DB_PATH}\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Vendors
    print("=== Vendors ===")
    vendors = cur.execute("SELECT * FROM vendors ORDER BY vendor_id").fetchall()
    for v in vendors:
        print(dict(v))
    print()

    # Brands
    print("=== Brands ===")
    brands = cur.execute("""
        SELECT b.brand_id, b.name, b.vendor_id, v.name AS vendor_name
        FROM brands b
        LEFT JOIN vendors v ON b.vendor_id = v.vendor_id
        ORDER BY b.brand_id
    """).fetchall()
    for b in brands:
        print(dict(b))
    print()

    # Categories
    print("=== Categories ===")
    categories = cur.execute("""
        SELECT c.category_id, c.name, c.vendor_id, v.name AS vendor_name
        FROM categories c
        LEFT JOIN vendors v ON c.vendor_id = v.vendor_id
        ORDER BY c.category_id
    """).fetchall()
    for c in categories:
        print(dict(c))
    print()

    # Shipping Tiers
    print("=== Shipping Tiers ===")
    shipping_tiers = cur.execute("""
        SELECT s.shipping_tier_id, s.shipping_tier, s.shipping_cost, s.vendor_id, v.name AS vendor_name
        FROM shipping_tiers s
        LEFT JOIN vendors v ON s.vendor_id = v.vendor_id
        ORDER BY s.shipping_tier_id
    """).fetchall()
    for s in shipping_tiers:
        print(dict(s))
    print()

    # Sample Products with Vendor, Brand, Category, Shipping Tier
    print("=== Products (sample) ===")
    sample_products = cur.execute("""
        SELECT 
            p.id, p.sku, p.name, 
            v.name AS vendor_name,
            b.name AS brand_name,
            c.name AS category_name,
            s.shipping_tier AS shipping_tier_name,
            p.cost, p.shipping_cost,
            p.extra_cost_applied, p.target_margin,
            p.calculated_price, p.calculated_raw_price,
            p.last_updated
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.vendor_id
        LEFT JOIN brands b ON p.brand_id = b.brand_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN shipping_tiers s ON p.shipping_tier_id = s.shipping_tier_id
        LIMIT 10
    """).fetchall()

    if sample_products:
        for p in sample_products:
            print(dict(p))
    else:
        print("No products found.")
    print()

    # Raw Products (full dump)
    print("=== Raw Products (direct dump) ===")
    all_products = cur.execute("SELECT * FROM products ORDER BY id").fetchall()
    if all_products:
        for p in all_products:
            pprint(dict(p))
    else:
        print("No rows in products table.")

    conn.close()


if __name__ == "__main__":
    inspect_db()
