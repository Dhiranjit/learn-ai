import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent.parent / "data" / "learn_ai.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Makes query accessible as row["name"]
    conn.execute("PRAGMA foreign_keys = ON") # Enables FOREIGN Key Enforcement
    return conn


def init_db() -> None:
    schema = SCHEMA_PATH.read_text()
    conn = get_connection()
    conn.executescript(schema)
    conn.close()