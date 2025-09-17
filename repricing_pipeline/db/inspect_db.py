import sqlite3
from tabulate import tabulate
from ..config import DB_PATH


def inspect_db(limit: int = 20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- Vendors table ---
    print("\n=== Vendors ===")
    vendors = cur.execute("SELECT id, name FROM vendors ORDER BY id").fetchall()
    if vendors:
        print(tabulate(vendors, headers=vendors[0].keys(), tablefmt="fancy_grid"))
    else:
        print("No vendors found.")

    # --- Products table (pretty join with vendors) ---
    print("\n=== Products (sample, joined with vendors) ===")
    products = cur.execute(
        """
        SELECT v.name AS vendor, p.sku, p.title, p.brand, p.category,
               p.cost, p.shipping_cost, p.shipping_tier_cost,
               p.extra_cost_applied, p.target_margin,
               p.calculated_raw_price, p.calculated_price,
               p.last_updated
        FROM products p
        LEFT JOIN vendors v ON p.vendor_id = v.id
        ORDER BY p.last_updated DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    if products:
        print(tabulate(products, headers=products[0].keys(), tablefmt="fancy_grid"))
    else:
        print("No products (sample) found.")

    # --- Raw product rows (debug view) ---
    print("\n=== Raw Products (direct dump) ===")
    rows = cur.execute("SELECT * FROM products LIMIT ?", (limit,)).fetchall()
    if rows:
        for r in rows:
            print(dict(r))
    else:
        print("No rows in products table.")

    conn.close()


if __name__ == "__main__":
    inspect_db()
