import threading
import sqlite3
from typing import Any, Dict

from wsqlite import WSQLite as Wsqlite_original

# Connection pooling for performance optimization
_db_connections: Dict[str, sqlite3.Connection] = {}
_db_lock = threading.RLock()