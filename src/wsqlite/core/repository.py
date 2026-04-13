"""Main repository class for SQLite operations with connection pooling."""

import logging
import re
from typing import Any, Callable, Optional

from pydantic import BaseModel

from wsqlite.core.connection import (
    AsyncTransaction,
    Transaction,
    get_async_connection,
    get_connection,
    get_transaction,
    retry_on_lock,
)
from wsqlite.core.pool import ConnectionPool, get_pool, close_pool
from wsqlite.core.sync import AsyncTableSync, TableSync
from wsqlite.exceptions import DatabaseLockedError, SQLInjectionError, TransactionError

logger = logging.getLogger(__name__)


def validate_identifier(identifier: str) -> None:
    """Validate SQL identifier to prevent SQL injection.

    Args:
        identifier: Table or column name to validate.

    Raises:
        SQLInjectionError: If identifier contains dangerous characters.
    """
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise SQLInjectionError(identifier)


class WSQLite:
    """SQLite repository using Pydantic models.

    Provides a simple interface for CRUD operations on SQLite tables,
    with automatic table creation, schema synchronization, and connection pooling.

    Example:
        from pydantic import BaseModel
        from wsqlite import WSQLite

        class User(BaseModel):
            id: int
            name: str
            email: str

        db = WSQLite(User, "database.db")
        db.insert(User(id=1, name="John", email="john@example.com"))
    """

    def __init__(
        self,
        model: type[BaseModel],
        db_path: str,
        pool_size: int = 10,
        min_pool_size: int = 2,
        use_pool: bool = True,
    ):
        """Initialize the repository with a Pydantic model.

        Args:
            model: Pydantic BaseModel class defining the table schema.
            db_path: Path to SQLite database file.
            pool_size: Maximum number of connections in pool.
            min_pool_size: Minimum number of connections in pool.
            use_pool: Whether to use connection pooling (recommended).
        """
        self.model = model
        self.db_path = db_path
        self.table_name = model.__name__.lower()
        self.use_pool = use_pool

        if use_pool:
            self._pool = get_pool(
                db_path,
                min_size=min_pool_size,
                max_size=pool_size,
            )
        else:
            self._pool = None

        self._sync = TableSync(model, db_path)
        self._sync.create_if_not_exists()
        self._sync.sync_with_model()

        logger.info(
            f"WSQLite initialized for table '{self.table_name}' (pool={use_pool}, size={pool_size})"
        )

    def _execute(self, query: str, values: tuple = (), commit: bool = True) -> Any:
        """Execute a query using pool or direct connection."""
        if self.use_pool and self._pool:
            with self._pool.connection() as conn:
                cursor = conn.execute(query, values)
                if cursor.description:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                if commit:
                    conn.commit()
                return result
        else:
            with get_connection(self.db_path) as conn:
                cursor = conn.execute(query, values)
                if cursor.description:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                if commit:
                    conn.commit()
                return result

    def insert(self, data: BaseModel) -> None:
        """Insert a new record into the database."""
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["?"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        self._execute(query, values)

    def get_all(self) -> list[BaseModel]:
        """Get all records from the table."""
        query = f"SELECT * FROM {self.table_name}"
        rows = self._execute(query, commit=False)

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_by_field(self, **filters) -> list[BaseModel]:
        """Get records filtered by specified fields."""
        if not filters:
            return self.get_all()

        conditions = " AND ".join(f"{key} = ?" for key in filters)
        values = tuple(filters.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        rows = self._execute(query, values, commit=False)

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def update(self, record_id: int, data: BaseModel) -> None:
        """Update a record in the database."""
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = ?" for key in data_dict.keys())
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = ?"

        self._execute(query, values)

    def delete(self, record_id: int) -> None:
        """Delete a record from the database."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self._execute(query, (record_id,))

    def _default_value(self, field: str) -> Any:
        """Get default value for a field when database value is NULL."""
        field_type = self.model.model_fields[field].annotation
        if field_type is str:
            return ""
        elif field_type is int:
            return 0
        elif field_type is bool:
            return False
        return None

    def get_paginated(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> list[BaseModel]:
        """Get records with pagination.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            order_by: Column to order by.
            order_desc: If True, order descending.

        Returns:
            List of model instances.
        """
        validate_identifier(self.table_name)
        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{order_clause} LIMIT ? OFFSET ?"

        rows = self._execute(query, (limit, offset), commit=False)

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_page(self, page: int = 1, per_page: int = 10) -> list[BaseModel]:
        """Get records by page number.

        Args:
            page: Page number (1-indexed).
            per_page: Number of records per page.

        Returns:
            List of model instances for the requested page.
        """
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        offset = (page - 1) * per_page
        return self.get_paginated(limit=per_page, offset=offset)

    def count(self) -> int:
        """Get total number of records in the table."""
        validate_identifier(self.table_name)
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self._execute(query, commit=False)
        return result[0][0] if result else 0

    def insert_many(self, data_list: list[BaseModel]) -> None:
        """Insert multiple records in a single transaction.

        Args:
            data_list: List of model instances to insert.
        """
        if not data_list:
            return

        data_dicts = [data.model_dump() for data in data_list]
        fields = ", ".join(data_dicts[0].keys())
        placeholders = ", ".join(["?"] * len(data_dicts[0]))

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        if self.use_pool and self._pool:
            with self._pool.connection() as conn:
                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    conn.execute(query, values)
                conn.commit()
        else:
            with get_transaction(self.db_path) as txn:
                for data_dict in data_dicts:
                    values = tuple(data_dict.values())
                    txn.execute(query, values)
                txn.commit()

    def update_many(self, updates: list[tuple[BaseModel, int]]) -> int:
        """Update multiple records.

        Args:
            updates: List of (model, record_id) tuples.

        Returns:
            Number of records updated.
        """
        if not updates:
            return 0

        validate_identifier(self.table_name)
        total_updated = 0

        if self.use_pool and self._pool:
            with self._pool.connection() as conn:
                for data, record_id in updates:
                    data_dict = data.model_dump()
                    fields = ", ".join(f"{key} = ?" for key in data_dict)
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = ?"
                    conn.execute(query, values)
                    total_updated += conn.total_changes
                conn.commit()
        else:
            with get_transaction(self.db_path) as txn:
                for data, record_id in updates:
                    data_dict = data.model_dump()
                    fields = ", ".join(f"{key} = ?" for key in data_dict)
                    values = tuple(data_dict.values()) + (record_id,)
                    query = f"UPDATE {self.table_name} SET {fields} WHERE id = ?"
                    txn.execute(query, values)
                    total_updated += txn.conn.total_changes
                txn.commit()

        return total_updated

    def delete_many(self, record_ids: list[int]) -> int:
        """Delete multiple records by their IDs.

        Args:
            record_ids: List of record IDs to delete.

        Returns:
            Number of records deleted.
        """
        if not record_ids:
            return 0

        validate_identifier(self.table_name)

        if self.use_pool and self._pool:
            with self._pool.connection() as conn:
                for record_id in record_ids:
                    query = f"DELETE FROM {self.table_name} WHERE id = ?"
                    conn.execute(query, (record_id,))
                conn.commit()
        else:
            with get_transaction(self.db_path) as txn:
                for record_id in record_ids:
                    query = f"DELETE FROM {self.table_name} WHERE id = ?"
                    txn.execute(query, (record_id,))
                txn.commit()

        return len(record_ids)

    def execute_transaction(self, operations: list[tuple[str, tuple]]) -> list[Any]:
        """Execute multiple operations in a transaction.

        Args:
            operations: List of (query, params) tuples.

        Returns:
            List of results from each operation.
        """
        results = []
        try:
            if self.use_pool and self._pool:
                with self._pool.connection() as conn:
                    for query, values in operations:
                        cursor = conn.execute(query, values)
                        if cursor.description:
                            results.append(cursor.fetchall())
                    conn.commit()
            else:
                with get_transaction(self.db_path) as txn:
                    for query, values in operations:
                        result = txn.execute(query, values)
                        if result is not None:
                            results.append(result)
                    txn.commit()
            logger.info(f"Transaction completed with {len(operations)} operations")
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise TransactionError(f"Transaction failed: {e}") from e
        return results

    def with_transaction(self, func: Callable[[Transaction], Any]) -> Any:
        """Execute a function within a transaction.

        Args:
            func: Function that receives Transaction and performs operations.

        Returns:
            Result of the function.
        """
        try:
            if self.use_pool and self._pool:
                with self._pool.connection() as conn:
                    txn = Transaction(self.db_path)
                    txn.conn = conn
                    result = func(txn)
                    conn.commit()
            else:
                with get_transaction(self.db_path) as txn:
                    result = func(txn)
                    txn.commit()
            logger.info("Transaction completed successfully")
            return result
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise TransactionError(f"Transaction failed: {e}") from e

    @retry_on_lock(max_retries=3, delay=0.1)
    def insert_with_retry(self, data: BaseModel) -> None:
        """Insert with automatic retry on database lock."""
        self.insert(data)

    async def insert_async(self, data: BaseModel) -> None:
        """Insert a new record into the database (async)."""
        data_dict = data.model_dump()
        fields = ", ".join(data_dict.keys())
        placeholders = ", ".join(["?"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        conn = await get_async_connection(self.db_path)
        try:
            await conn.execute(query, values)
            await conn.commit()
        finally:
            await conn.close()

    async def get_all_async(self) -> list[BaseModel]:
        """Get all records from the table (async)."""
        query = f"SELECT * FROM {self.table_name}"
        conn = await get_async_connection(self.db_path)
        try:
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()
        finally:
            await conn.close()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    async def get_by_field_async(self, **filters) -> list[BaseModel]:
        """Get records filtered by specified fields (async)."""
        if not filters:
            return await self.get_all_async()

        conditions = " AND ".join(f"{key} = ?" for key in filters)
        values = tuple(filters.values())
        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        conn = await get_async_connection(self.db_path)
        try:
            cursor = await conn.execute(query, values)
            rows = await cursor.fetchall()
        finally:
            await conn.close()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    async def update_async(self, record_id: int, data: BaseModel) -> None:
        """Update a record in the database (async)."""
        data_dict = data.model_dump()
        fields = ", ".join(f"{key} = ?" for key in data_dict.keys())
        values = tuple(data_dict.values()) + (record_id,)
        query = f"UPDATE {self.table_name} SET {fields} WHERE id = ?"

        conn = await get_async_connection(self.db_path)
        try:
            await conn.execute(query, values)
            await conn.commit()
        finally:
            await conn.close()

    async def delete_async(self, record_id: int) -> None:
        """Delete a record from the database (async)."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        conn = await get_async_connection(self.db_path)
        try:
            await conn.execute(query, (record_id,))
            await conn.commit()
        finally:
            await conn.close()

    async def get_paginated_async(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> list[BaseModel]:
        """Get records with pagination (async)."""
        validate_identifier(self.table_name)
        if order_by:
            validate_identifier(order_by)
            order_clause = f" ORDER BY {order_by} {'DESC' if order_desc else 'ASC'}"
        else:
            order_clause = ""

        query = f"SELECT * FROM {self.table_name}{order_clause} LIMIT ? OFFSET ?"

        conn = await get_async_connection(self.db_path)
        try:
            cursor = await conn.execute(query, (limit, offset))
            rows = await cursor.fetchall()
        finally:
            await conn.close()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    async def get_page_async(self, page: int = 1, per_page: int = 10) -> list[BaseModel]:
        """Get records by page number (async)."""
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
        offset = (page - 1) * per_page
        return await self.get_paginated_async(limit=per_page, offset=offset)

    async def count_async(self) -> int:
        """Get total number of records in the table (async)."""
        validate_identifier(self.table_name)
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        conn = await get_async_connection(self.db_path)
        try:
            cursor = await conn.execute(query)
            result = await cursor.fetchone()
        finally:
            await conn.close()
        return result[0] if result else 0

    async def insert_many_async(self, data_list: list[BaseModel]) -> None:
        """Insert multiple records in a single transaction (async)."""
        if not data_list:
            return

        data_dicts = [data.model_dump() for data in data_list]
        fields = ", ".join(data_dicts[0].keys())
        placeholders = ", ".join(["?"] * len(data_dicts[0]))

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        conn = await get_async_connection(self.db_path)
        try:
            for data_dict in data_dicts:
                values = tuple(data_dict.values())
                await conn.execute(query, values)
            await conn.commit()
        finally:
            await conn.close()

    async def update_many_async(self, updates: list[tuple[BaseModel, int]]) -> int:
        """Update multiple records (async)."""
        if not updates:
            return 0

        validate_identifier(self.table_name)
        total_updated = 0

        conn = await get_async_connection(self.db_path)
        try:
            for data, record_id in updates:
                data_dict = data.model_dump()
                fields = ", ".join(f"{key} = ?" for key in data_dict)
                values = tuple(data_dict.values()) + (record_id,)
                query = f"UPDATE {self.table_name} SET {fields} WHERE id = ?"
                await conn.execute(query, values)
                total_updated += conn.total_changes
            await conn.commit()
        finally:
            await conn.close()

        return total_updated

    async def delete_many_async(self, record_ids: list[int]) -> int:
        """Delete multiple records by their IDs (async)."""
        if not record_ids:
            return 0

        validate_identifier(self.table_name)

        conn = await get_async_connection(self.db_path)
        try:
            for record_id in record_ids:
                query = f"DELETE FROM {self.table_name} WHERE id = ?"
                await conn.execute(query, (record_id,))
            await conn.commit()
        finally:
            await conn.close()

        return len(record_ids)

    async def execute_transaction_async(self, operations: list[tuple[str, tuple]]) -> list[Any]:
        """Execute multiple operations in a transaction (async)."""
        results = []
        conn = await get_async_connection(self.db_path)
        try:
            for query, values in operations:
                cursor = await conn.execute(query, values)
                if cursor.description:
                    result = await cursor.fetchall()
                    results.append(result)
            await conn.commit()
            logger.info(f"Async transaction completed with {len(operations)} operations")
        except Exception as e:
            logger.error(f"Async transaction failed: {e}")
            await conn.close()
            raise TransactionError(f"Async transaction failed: {e}") from e
        finally:
            if not conn._connection:  # not closed yet
                await conn.close()
        return results

    async def with_transaction_async(self, func: Callable[[AsyncTransaction], Any]) -> Any:
        """Execute a function within a transaction (async)."""
        try:
            conn = await get_async_connection(self.db_path)
            async with conn:
                txn = AsyncTransaction(self.db_path)
                txn.conn = conn
                result = await func(txn)
                await txn.commit()
                logger.info("Async transaction completed successfully")
                return result
        except Exception as e:
            logger.error(f"Async transaction failed: {e}")
            raise TransactionError(f"Async transaction failed: {e}") from e
