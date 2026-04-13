"""Tests for connection module."""

import os
import sqlite3
import tempfile
import time
import uuid

import pytest
from unittest.mock import Mock, patch, MagicMock

from wsqlite.core.connection import (
    Transaction,
    AsyncTransaction,
    get_transaction,
    get_async_transaction,
    get_connection,
    _SQLiteConnection,
    close_global_connection,
    retry_on_lock,
    get_async_connection,
)
from wsqlite.core.pool import close_pool


@pytest.fixture
def db_path():
    """Unique database path for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, f"test_{uuid.uuid4().hex[:8]}.db")
    close_pool()


class TestSQLiteConnection:
    """Tests for _SQLiteConnection wrapper."""

    def test_enter_returns_conn(self):
        mock_conn = MagicMock()
        wrapper = _SQLiteConnection(mock_conn)
        result = wrapper.__enter__()
        assert result is mock_conn

    def test_exit_does_nothing(self):
        mock_conn = MagicMock()
        wrapper = _SQLiteConnection(mock_conn)
        wrapper.__exit__(None, None, None)
        mock_conn.close.assert_not_called()

    def test_getattr_delegates(self):
        mock_conn = MagicMock()
        mock_conn.some_method.return_value = "result"
        wrapper = _SQLiteConnection(mock_conn)
        assert wrapper.some_method() == "result"


class TestTransaction:
    """Tests for Transaction class."""

    def test_transaction_context_commit(self, db_path):
        """Test transaction commits on successful exit."""
        with Transaction(db_path) as txn:
            pass
        assert os.path.exists(db_path)

    def test_transaction_context_rollback_on_exception(self, db_path):
        """Test transaction rolls back on exception."""
        with pytest.raises(ValueError):
            with Transaction(db_path) as txn:
                raise ValueError("Test error")

    def test_manual_commit(self, db_path):
        """Test manual commit."""
        with Transaction(db_path) as txn:
            txn.commit()
            assert txn._committed is True

    def test_manual_rollback(self, db_path):
        """Test manual rollback."""
        with Transaction(db_path) as txn:
            txn.rollback()

    def test_execute_query(self, db_path):
        """Test executing query within transaction."""
        with Transaction(db_path) as txn:
            result = txn.execute("CREATE TABLE test (id INTEGER)", ())
        assert os.path.exists(db_path)

    def test_execute_with_values(self, db_path):
        """Test executing query with values."""
        with Transaction(db_path) as txn:
            txn.execute("CREATE TABLE test (id INTEGER, name TEXT)", ())
            txn.execute("INSERT INTO test VALUES (?, ?)", (1, "Alice"))
            result = txn.execute("SELECT * FROM test", ())
        assert len(result) == 1
        assert result[0][1] == "Alice"

    def test_execute_without_result(self, db_path):
        """Test executing query without result (DDL)."""
        with Transaction(db_path) as txn:
            result = txn.execute("CREATE TABLE test2 (id INTEGER)", ())
        assert result == -1

    def test_execute_insert_returns_rowcount(self, db_path):
        """Test execute returns rowcount for INSERT."""
        with Transaction(db_path) as txn:
            txn.execute("CREATE TABLE test3 (id INTEGER)", ())
            result = txn.execute("INSERT INTO test3 VALUES (1)", ())
        assert result == 1

    def test_execute_update_returns_rowcount(self, db_path):
        """Test execute returns rowcount for UPDATE."""
        with Transaction(db_path) as txn:
            txn.execute("CREATE TABLE test4 (id INTEGER, value TEXT)", ())
            txn.execute("INSERT INTO test4 VALUES (1, 'a')", ())
            txn.execute("INSERT INTO test4 VALUES (2, 'b')", ())
            result = txn.execute("UPDATE test4 SET value='c' WHERE id=1", ())
        assert result == 1

    def test_transaction_initial_state(self, db_path):
        """Test transaction initial state."""
        txn = Transaction(db_path)
        assert txn.db_path == db_path
        assert txn.conn is None
        assert txn._committed is False

    def test_execute_with_empty_values(self, db_path):
        """Test execute with empty tuple."""
        with Transaction(db_path) as txn:
            txn.execute("CREATE TABLE test_empty (id INTEGER)", ())
            result = txn.execute("SELECT * FROM test_empty", ())
        assert result == []


class TestGetTransaction:
    """Tests for get_transaction helper."""

    def test_get_transaction(self, db_path):
        """Test get_transaction returns Transaction context manager."""
        with get_transaction(db_path) as txn:
            assert isinstance(txn, Transaction)


class TestRetryOnLock:
    """Tests for retry_on_lock decorator."""

    def test_successful_call(self):
        """Test successful call without retries."""

        @retry_on_lock(max_retries=3)
        def success_func():
            return "success"

        assert success_func() == "success"

    def test_retry_on_lock(self):
        """Test retry on database lock."""
        call_count = 0

        @retry_on_lock(max_retries=3, delay=0.01)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise sqlite3.OperationalError("database is locked")
            return "success"

        assert flaky_func() == "success"
        assert call_count == 3

    def test_no_retry_on_other_error(self):
        """Test no retry on non-lock errors."""

        @retry_on_lock(max_retries=3)
        def error_func():
            raise ValueError("some other error")

        with pytest.raises(ValueError):
            error_func()

    def test_max_retries_exceeded(self):
        """Test max retries exceeded."""

        @retry_on_lock(max_retries=2, delay=0.01)
        def always_fails():
            raise sqlite3.OperationalError("database is locked")

        with pytest.raises(sqlite3.OperationalError):
            always_fails()


class TestGetConnection:
    """Tests for get_connection function."""

    def test_get_connection_returns_wrapper(self, db_path):
        """Test get_connection returns _SQLiteConnection wrapper."""
        conn = get_connection(db_path)
        assert isinstance(conn, _SQLiteConnection)

    def test_get_connection_executes_query(self, db_path):
        """Test connection can execute queries."""
        with get_connection(db_path) as conn:
            conn.execute("CREATE TABLE test_get (id INTEGER)", ())
            conn.commit()

        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT * FROM test_get")
        assert cursor.fetchall() == []
        conn.close()


class TestCloseGlobalConnection:
    """Tests for close_global_connection function."""

    def test_close_global_connection(self, db_path):
        """Test close_global_connection runs without error."""
        get_connection(db_path)
        close_global_connection()
        get_connection(db_path)
        close_global_connection()


class TestAsyncTransaction:
    """Tests for AsyncTransaction class."""

    def test_async_transaction_init(self, db_path):
        """Test AsyncTransaction initialization."""
        txn = AsyncTransaction(db_path)
        assert txn.db_path == db_path
        assert txn.conn is None
        assert txn._committed is False


class TestGetAsyncTransaction:
    """Tests for get_async_transaction function."""

    def test_get_async_transaction_exists(self):
        """Test get_async_transaction function exists."""
        assert callable(get_async_transaction)


class TestGetAsyncConnection:
    """Tests for get_async_connection function."""

    def test_get_async_connection_exists(self):
        """Test get_async_connection function exists."""
        assert callable(get_async_connection)
