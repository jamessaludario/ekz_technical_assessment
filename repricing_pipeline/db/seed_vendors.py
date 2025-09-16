# repricing_pipeline/db/seed_vendors.py
import sqlite3
from repricing_pipeline.config import DB_PATH

VENDORS = [
    {"id": 1, "name": "Evergreen Merchants"},
    {"id": 2, "name": "Titan Labs"},
    {"id": 3, "name": "Prime Distributors"},
    {"id": 4, "name": "Pacific Supply Group"},
    {"id": 5, "name": "Brightside Trading"},
]

def seed_vendors():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for v in VENDORS:
        cur.execute(
            "INSERT OR IGNORE INTO vendors (id, name) VALUES (?, ?)",
            (v["id"], v["name"]),
        )
    conn.commit()
    conn.close()
    print("Vendors seeded.")

if __name__ == "__main__":
    seed_vendors()
