# repricing_pipeline/db/seed_vendors.py
import sqlite3
from repricing_pipeline.config import DB_PATH

VENDORS = [
    {"vendor_id": 1, "name": "Evergreen Merchants"},
    {"vendor_id": 2, "name": "Titan Labs"},
    {"vendor_id": 3, "name": "Prime Distributors"},
    {"vendor_id": 4, "name": "Pacific Supply Group"},
    {"vendor_id": 5, "name": "Brightside Trading"},
]

def seed_vendors():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for v in VENDORS:
        cur.execute(
            """
            INSERT INTO vendors (vendor_id, name)
            VALUES (?, ?)
            ON CONFLICT(vendor_id) DO UPDATE SET name=excluded.name
            """,
            (v["vendor_id"], v["name"]),
        )
    conn.commit()
    conn.close()
    print("Vendors seeded.")

if __name__ == "__main__":
    seed_vendors()
