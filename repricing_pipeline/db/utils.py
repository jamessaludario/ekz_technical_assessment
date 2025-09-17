import sqlite3
from ..config import DB_PATH

def get_vendors():
    """Return vendors as a dict {name: id} from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute("SELECT id, name FROM vendors ORDER BY id").fetchall()
    conn.close()

    return {row["name"]: row["id"] for row in rows}
