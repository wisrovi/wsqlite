"""wsqlite - SQLite ORM using Pydantic models.

A simple and type-safe SQLite ORM that uses Pydantic models
to define database schemas. Automatically handles table creation,
synchronization, CRUD operations, and connection pooling.

Usage:
    from wsqlite import WSQLite

    class User(BaseModel):
        id: int
        name: str
        email: str

    db = WSQLite(User, "database.db")
    db.insert(User(id=1, name="John", email="john@example.com"))

Async usage:
    await db.insert_async(User(id=1, name="John", email="john@example.com"))
    users = await db.get_all_async()

Connection Pooling:
    db = WSQLite(User, "database.db", pool_size=20)
"""

from wsqlite.builders import QueryBuilder
from wsqlite.core.connection import (
    AsyncTransaction,
    Transaction,
    get_async_connection,
    get_async_transaction,
    get_connection,
    get_transaction,
    retry_on_lock,
)
from wsqlite.core.pool import (
    AsyncConnectionPool,
    ConnectionPool,
    close_all_pools,
    close_async_pool,
    close_pool,
    get_async_pool,
    get_pool,
)
from wsqlite.core.repository import ForensicModel, WSQLite as WSQLiteImpl
from wsqlite.core.sync import AsyncTableSync, TableSync
from wsqlite.views import view

__version__ = "1.4.0"

WSQLite = WSQLiteImpl

__all__ = [
    "WSQLite",
    "ForensicModel",
    "view",
    "QueryBuilder",
    "Transaction",
    "AsyncTransaction",
    "get_connection",
    "get_async_connection",
    "get_transaction",

    "get_async_transaction",
    "retry_on_lock",
    "TableSync",
    "AsyncTableSync",
    "ConnectionPool",
    "AsyncConnectionPool",
    "get_pool",
    "get_async_pool",
    "close_pool",
    "close_async_pool",
    "close_all_pools",
    "WSQLiteError",
    "ConnectionError",
    "PoolExhaustedError",
    "DatabaseLockedError",
    "TableSyncError",
    "ValidationError",
    "OperationError",
    "SQLInjectionError",
    "TransactionError",
    "MigrationError",
    "QueryError",
    "TimeoutError",
]

WSQLite = WSQLiteImpl
