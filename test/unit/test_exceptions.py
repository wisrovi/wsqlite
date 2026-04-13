"""Tests for exceptions module."""

import pytest

from wsqlite.exceptions import (
    WSQLiteError,
    ConnectionError,
    PoolExhaustedError,
    DatabaseLockedError,
    TableSyncError,
    ValidationError,
    OperationError,
    SQLInjectionError,
    TransactionError,
    MigrationError,
    QueryError,
    TimeoutError,
)


class TestWSQLiteError:
    """Tests for base WSQLiteError class."""

    def test_creation_with_message(self):
        err = WSQLiteError("Test error")
        assert str(err) == "Test error"
        assert err.message == "Test error"
        assert err.details == {}

    def test_creation_with_details(self):
        err = WSQLiteError("Test error", {"key": "value"})
        assert err.details == {"key": "value"}

    def test_inheritance(self):
        err = WSQLiteError("test")
        assert isinstance(err, Exception)


class TestPoolExhaustedError:
    """Tests for PoolExhaustedError class."""

    def test_error_message_contains_info(self):
        err = PoolExhaustedError(max_size=10, timeout=30.0)
        message = str(err)
        assert "10" in message
        assert "30" in message
        assert "exhausted" in message.lower()

    def test_error_has_attributes(self):
        err = PoolExhaustedError(max_size=10, timeout=30.0)
        assert err.max_size == 10
        assert err.timeout == 30.0

    def test_inheritance(self):
        err = PoolExhaustedError(5)
        assert isinstance(err, ConnectionError)
        assert isinstance(err, WSQLiteError)


class TestDatabaseLockedError:
    """Tests for DatabaseLockedError class."""

    def test_error_message(self):
        err = DatabaseLockedError(operation="INSERT")
        message = str(err)
        assert "INSERT" in message
        assert "locked" in message.lower()

    def test_error_with_query(self):
        err = DatabaseLockedError(operation="SELECT", query="SELECT * FROM users")
        assert err.operation == "SELECT"
        assert err.query == "SELECT * FROM users"

    def test_inheritance(self):
        err = DatabaseLockedError("test")
        assert isinstance(err, ConnectionError)
        assert isinstance(err, WSQLiteError)


class TestTableSyncError:
    """Tests for TableSyncError class."""

    def test_creation(self):
        err = TableSyncError("Table sync failed")
        assert "sync" in str(err).lower()

    def test_inheritance(self):
        err = TableSyncError("test")
        assert isinstance(err, WSQLiteError)


class TestValidationError:
    """Tests for ValidationError class."""

    def test_creation(self):
        err = ValidationError("Invalid data")
        assert "Invalid data" in str(err)

    def test_inheritance(self):
        err = ValidationError("test")
        assert isinstance(err, WSQLiteError)


class TestOperationError:
    """Tests for OperationError class."""

    def test_creation_simple(self):
        err = OperationError("Operation failed")
        assert "failed" in str(err).lower()

    def test_creation_with_query(self):
        err = OperationError("Query failed", query="SELECT * FROM users")
        assert err.query == "SELECT * FROM users"

    def test_creation_with_params(self):
        err = OperationError("Query failed", query="?", params=(1, 2, 3))
        assert err.params == (1, 2, 3)

    def test_inheritance(self):
        err = OperationError("test")
        assert isinstance(err, WSQLiteError)


class TestSQLInjectionError:
    """Tests for SQLInjectionError class."""

    def test_error_message(self):
        err = SQLInjectionError("users; DROP TABLE users")
        message = str(err)
        assert "users; DROP TABLE users" in message
        assert "dangerous" in message.lower()
        assert "identifier" in message.lower()

    def test_error_has_identifier_attribute(self):
        dangerous = "'; DROP TABLE users;--"
        err = SQLInjectionError(dangerous)
        assert err.identifier == dangerous

    def test_inheritance(self):
        err = SQLInjectionError("test")
        assert isinstance(err, WSQLiteError)


class TestTransactionError:
    """Tests for TransactionError class."""

    def test_creation(self):
        err = TransactionError("Transaction failed")
        assert "failed" in str(err).lower()

    def test_inheritance(self):
        err = TransactionError("test")
        assert isinstance(err, WSQLiteError)


class TestMigrationError:
    """Tests for MigrationError class."""

    def test_creation_simple(self):
        err = MigrationError("Migration failed")
        assert "failed" in str(err).lower()

    def test_creation_with_version(self):
        err = MigrationError("Version conflict", version=5, direction="up")
        assert err.version == 5
        assert err.direction == "up"

    def test_inheritance(self):
        err = MigrationError("test")
        assert isinstance(err, WSQLiteError)


class TestQueryError:
    """Tests for QueryError class."""

    def test_creation_simple(self):
        err = QueryError("Query syntax error")
        assert "syntax" in str(err).lower()

    def test_creation_with_query(self):
        err = QueryError("Query failed", query="INVALID SQL")
        assert err.query == "INVALID SQL"

    def test_creation_with_original_error(self):
        original = ValueError("original error")
        err = QueryError("Wrapped", original_error=original)
        assert err.original_error is original

    def test_inheritance(self):
        err = QueryError("test")
        assert isinstance(err, WSQLiteError)


class TestTimeoutError:
    """Tests for TimeoutError class."""

    def test_error_message(self):
        err = TimeoutError(operation="SELECT", timeout=30.0)
        message = str(err)
        assert "SELECT" in message
        assert "30" in message
        assert "timeout" in message.lower()

    def test_error_has_attributes(self):
        err = TimeoutError("test", 60.0)
        assert err.operation == "test"
        assert err.timeout == 60.0

    def test_inheritance(self):
        err = TimeoutError("test", 30)
        assert isinstance(err, WSQLiteError)


class TestExceptionInheritance:
    """Tests that all exceptions inherit from WSQLiteError."""

    def test_all_exceptions_inherit(self):
        exceptions = [
            ConnectionError("test"),
            PoolExhaustedError(5),
            DatabaseLockedError("test"),
            TableSyncError("test"),
            ValidationError("test"),
            OperationError("test"),
            SQLInjectionError("test"),
            TransactionError("test"),
            MigrationError("test"),
            QueryError("test"),
            TimeoutError("test", 30),
        ]

        for err in exceptions:
            assert isinstance(err, WSQLiteError)
            assert isinstance(err, Exception)


class TestExceptionCatching:
    """Tests for catching exceptions correctly."""

    def test_catch_connection_error(self):
        with pytest.raises(ConnectionError):
            raise PoolExhaustedError(5)

    def test_catch_wsqlite_error(self):
        with pytest.raises(WSQLiteError):
            raise ValidationError("test")

    def test_catch_any_wsqlite_exception(self):
        with pytest.raises(WSQLiteError):
            raise SQLInjectionError("test")

    def test_exception_chain(self):
        original = ValueError("original")
        try:
            raise QueryError("wrapped", original_error=original)
        except QueryError as e:
            assert e.original_error is original
