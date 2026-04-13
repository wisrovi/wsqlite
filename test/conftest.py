import os
import tempfile

DB_PATH = os.path.join(tempfile.gettempdir(), "test_wsqlite.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


def setup_function():
    """Clean up before each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def teardown_function():
    """Clean up after each test."""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    except Exception:
        pass


def cleanup_table(table_name: str):
    """Clean up a table."""
    try:
        import sqlite3

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        conn.close()
    except Exception:
        pass
