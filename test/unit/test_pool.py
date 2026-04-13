"""Tests for connection pool module."""

import os
import sqlite3
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from wsqlite.core.pool import (
    ConnectionPool,
    AsyncConnectionPool,
    PoolExhaustedError,
    DatabaseLockedError,
    get_pool,
    close_pool,
    close_all_pools,
    get_async_pool,
)


class TestConnectionPool:
    """Tests for ConnectionPool class."""

    @pytest.fixture
    def db_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "test.db")

    @pytest.fixture
    def pool(self, db_path):
        p = ConnectionPool(db_path, min_size=2, max_size=5, timeout=5.0)
        yield p
        p.close_all()

    def test_init_creates_min_connections(self, db_path):
        pool = ConnectionPool(db_path, min_size=3, max_size=10)
        try:
            assert len(pool) == 3
            assert pool.stats["current_size"] == 3
            assert pool.stats["min_size"] == 3
            assert pool.stats["max_size"] == 10
        finally:
            pool.close_all()

    def test_wal_mode_enabled_by_default(self, db_path):
        pool = ConnectionPool(db_path)
        try:
            with pool.connection() as conn:
                cursor = conn.execute("PRAGMA journal_mode")
                result = cursor.fetchone()[0]
                assert result.upper() == "WAL"
        finally:
            pool.close_all()

    def test_get_connection_returns_working_connection(self, pool):
        conn = pool.get_connection()
        try:
            assert pool._is_healthy(conn) is True
        finally:
            pool.return_connection(conn)

    def test_return_connection_returns_to_pool(self, pool):
        conn = pool.get_connection()
        pool.return_connection(conn)
        assert len(pool) == 2  # Back to min size

    def test_connection_context_manager(self, pool):
        with pool.connection() as conn:
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()[0]
            assert result == 1

    def test_pool_exhausted_error(self, db_path):
        pool = ConnectionPool(db_path, min_size=1, max_size=2, timeout=0.5)
        try:
            conn1 = pool.get_connection()
            conn2 = pool.get_connection()
            with pytest.raises(PoolExhaustedError) as exc_info:
                pool.get_connection(timeout=0.1)
            assert "exhausted" in str(exc_info.value).lower()
            pool.return_connection(conn1)
            pool.return_connection(conn2)
        finally:
            pool.close_all()

    def test_unhealthy_connection_replaced(self, db_path):
        pool = ConnectionPool(db_path, min_size=1, max_size=2)
        try:
            conn = pool.get_connection()
            closed_conn = sqlite3.connect(db_path)
            closed_conn.close()

            pool.return_connection(conn)

            new_conn = pool.get_connection()
            assert pool._is_healthy(new_conn)
            pool.return_connection(new_conn)
        finally:
            pool.close_all()

    def test_concurrent_access(self, db_path):
        pool = ConnectionPool(db_path, min_size=5, max_size=10)
        try:
            with pool.connection() as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")

            results = []

            def worker(worker_id):
                for i in range(10):
                    with pool.connection() as conn:
                        conn.execute("INSERT INTO test (name) VALUES (?)", (f"w{worker_id}_{i}",))
                        conn.commit()
                        results.append(1)

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(worker, i) for i in range(5)]
                for f in futures:
                    f.result()

            assert len(results) == 50
        finally:
            pool.close_all()

    def test_close_all_closes_connections(self, db_path):
        pool = ConnectionPool(db_path, min_size=3, max_size=5)
        assert len(pool) == 3

        pool.close_all()
        assert len(pool) == 0
        assert pool.stats["closed"] is True

    def test_pool_context_manager(self, db_path):
        with ConnectionPool(db_path) as pool:
            with pool.connection() as conn:
                cursor = conn.execute("SELECT 1")
                assert cursor.fetchone()[0] == 1

        assert pool._closed is True

    def test_stats_property(self, pool):
        stats = pool.stats
        assert "pool_id" in stats
        assert "db_path" in stats
        assert "current_size" in stats
        assert "min_size" in stats
        assert "max_size" in stats
        assert "available" in stats

    def test_multiple_pools_same_db_returns_same(self, db_path):
        close_pool()
        pool1 = get_pool(db_path, min_size=2, max_size=5)
        pool2 = get_pool(db_path, min_size=2, max_size=5)
        assert pool1 is pool2
        close_pool()

    def test_different_db_returns_different_pool(self):
        close_pool()
        with tempfile.TemporaryDirectory() as tmpdir:
            pool1 = get_pool(os.path.join(tmpdir, "db1.db"))
            pool2 = get_pool(os.path.join(tmpdir, "db2.db"))
            assert pool1 is not pool2
        close_pool()

    def test_busy_timeout_configured(self, pool):
        with pool.connection() as conn:
            cursor = conn.execute("PRAGMA busy_timeout")
            result = cursor.fetchone()[0]
            assert result == 5000

    def test_synchronous_configured(self, pool):
        with pool.connection() as conn:
            cursor = conn.execute("PRAGMA synchronous")
            result = cursor.fetchone()[0]
            assert result == 1

    def test_cache_size_configured(self, pool):
        with pool.connection() as conn:
            cursor = conn.execute("PRAGMA cache_size")
            result = cursor.fetchone()[0]
            assert result == -2000

    def test_get_connection_closed_pool_raises(self, db_path):
        pool = ConnectionPool(db_path)
        pool.close_all()
        with pytest.raises(RuntimeError, match="closed"):
            pool.get_connection()

    def test_get_connection_wait_time_logged(self, db_path):
        pool = ConnectionPool(db_path, min_size=1, max_size=1, timeout=5.0)
        try:
            conn1 = pool.get_connection()

            def delayed_return():
                time.sleep(0.2)
                pool.return_connection(conn1)

            thread = threading.Thread(target=delayed_return)
            thread.start()

            conn2 = pool.get_connection()
            pool.return_connection(conn2)

            thread.join()
        finally:
            pool.close_all()

    def test_execute_query_with_results(self, db_path):
        pool = ConnectionPool(db_path)
        try:
            pool.execute("CREATE TABLE test_exec (id INTEGER)")
            pool.execute("INSERT INTO test_exec VALUES (1)")
            pool.execute("INSERT INTO test_exec VALUES (2)")

            result = pool.execute("SELECT * FROM test_exec")
            assert len(result) == 2
        finally:
            pool.close_all()

    def test_execute_query_without_results(self, db_path):
        pool = ConnectionPool(db_path)
        try:
            result = pool.execute("CREATE TABLE test_no_res (id INTEGER)")
            assert result == -1
        finally:
            pool.close_all()

    def test_execute_query_no_commit(self, db_path):
        pool = ConnectionPool(db_path)
        try:
            pool.execute("CREATE TABLE test_no_commit (id INTEGER)")
            result = pool.execute("INSERT INTO test_no_commit VALUES (1)", commit=False)
            assert result == 1
        finally:
            pool.close_all()

    def test_pool_id_unique(self, db_path):
        pool1 = ConnectionPool(db_path, min_size=1, max_size=1)
        pool2 = ConnectionPool(db_path, min_size=1, max_size=1)
        assert pool1._pool_id != pool2._pool_id
        pool1.close_all()
        pool2.close_all()

    def test_is_healthy_with_invalid_connection(self):
        pool = ConnectionPool.__new__(ConnectionPool)
        pool._size = 0
        conn = sqlite3.connect(":memory:")
        conn.close()
        assert pool._is_healthy(conn) is False


class TestAsyncConnectionPool:
    """Tests for AsyncConnectionPool class."""

    @pytest.fixture
    def db_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "test_async.db")

    def test_async_pool_sync_init(self, db_path):
        pool = AsyncConnectionPool.__new__(AsyncConnectionPool)
        pool.db_path = db_path
        pool.min_size = 2
        pool.max_size = 5
        assert pool.db_path == db_path

    def test_async_pool_attributes(self, db_path):
        pool = AsyncConnectionPool.__new__(AsyncConnectionPool)
        pool.db_path = db_path
        pool.min_size = 2
        pool.max_size = 5
        pool._pool_id = "test123"
        assert pool._pool_id == "test123"


class TestGlobalPoolFunctions:
    """Tests for global pool management functions."""

    def test_close_pool_resets_global(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            pool = get_pool(db_path)
            assert pool is not None
            close_pool()

    def test_close_all_pools(self):
        close_all_pools()

    def test_get_pool_with_custom_params(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            pool = get_pool(db_path, min_size=3, max_size=15)
            assert pool.min_size == 3
            assert pool.max_size == 15
            close_pool()

    def test_get_async_pool(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            pool = get_async_pool(db_path)
            assert pool is not None


class TestPoolExhaustedError:
    """Tests for PoolExhaustedError exception."""

    def test_error_message(self):
        error = PoolExhaustedError(max_size=10, timeout=5.0)
        assert "exhausted" in str(error).lower()
        assert error.max_size == 10
        assert error.timeout == 5.0


class TestDatabaseLockedError:
    """Tests for DatabaseLockedError exception."""

    def test_error_message(self):
        error = DatabaseLockedError(operation="INSERT")
        assert "locked" in str(error).lower()
        assert error.operation == "INSERT"
