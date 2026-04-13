"""Tests for migrations module."""

import os
import tempfile

import pytest

from wsqlite.migrations import (
    MigrationManager,
    Migration,
    AppliedMigration,
    create_migration_manager,
)
from wsqlite.exceptions import MigrationError


class TestMigrationManager:
    """Tests for MigrationManager class."""

    @pytest.fixture
    def db_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "test.db")

    @pytest.fixture
    def manager(self, db_path):
        return MigrationManager(db_path)

    def test_init_creates_migrations_table(self, db_path):
        import sqlite3

        mgr = MigrationManager(db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='_schema_migrations'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None

    def test_register_migration(self, manager):
        def up(ctx):
            ctx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

        manager.register(1, "Create test table", up)

        assert 1 in manager._migrations
        assert manager._migrations[1].description == "Create test table"

    def test_register_duplicate_version_raises(self, manager):
        def up(ctx):
            ctx.execute("CREATE TABLE test (id INTEGER)")

        manager.register(1, "First", up)

        with pytest.raises(MigrationError, match="already registered"):
            manager.register(1, "Second", up)

    def test_decorator_registers_migration(self, manager):
        @manager.migration(1, "Test migration")
        def migrate(ctx):
            pass

        assert 1 in manager._migrations

    def test_decorator_allow_down_false(self, manager):
        @manager.migration(1, "Test", allow_down=False)
        def migrate(ctx):
            pass

        # allow_down doesn't affect down function - it just tracks preference
        # The actual down function is set via the decorator or register()
        assert manager._migrations[1].version == 1

    def test_get_current_version_empty(self, manager):
        assert manager.get_current_version() == 0

    def test_get_current_version_after_migration(self, db_path):
        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE _schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        """)
        conn.execute(
            "INSERT INTO _schema_migrations VALUES (?, ?, ?)", (1, "Test", "2024-01-01T00:00:00")
        )
        conn.commit()
        conn.close()

        mgr = MigrationManager(db_path)
        assert mgr.get_current_version() == 1

    def test_get_applied_migrations(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def up2(ctx):
            ctx.execute("CREATE TABLE t2 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.register(2, "Create t2", up2)

        applied = manager.get_applied_migrations()
        assert len(applied) == 0

    def test_get_pending_migrations(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def up2(ctx):
            ctx.execute("CREATE TABLE t2 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.register(2, "Create t2", up2)

        pending = manager.get_pending_migrations()
        assert len(pending) == 2
        assert pending[0].version == 1
        assert pending[1].version == 2

    def test_migrate_up_applies_migrations(self, manager):
        migrations_run = []

        def up1(ctx):
            ctx.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
            migrations_run.append(1)

        def up2(ctx):
            ctx.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER)")
            migrations_run.append(2)

        manager.register(1, "Create users", up1)
        manager.register(2, "Create orders", up2)

        applied = manager.migrate_up()

        assert len(applied) == 2
        assert 1 in migrations_run
        assert 2 in migrations_run
        assert manager.get_current_version() == 2

    def test_migrate_up_to_specific_version(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def up2(ctx):
            ctx.execute("CREATE TABLE t2 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.register(2, "Create t2", up2)

        applied = manager.migrate_up(target_version=1)

        assert len(applied) == 1
        assert applied[0].version == 1
        assert manager.get_current_version() == 1

    def test_migrate_up_idempotent(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        manager.register(1, "Create t1", up1)

        manager.migrate_up()
        first_version = manager.get_current_version()

        applied = manager.migrate_up()
        second_version = manager.get_current_version()

        assert len(applied) == 0
        assert first_version == second_version == 1

    def test_migrate_down_rolls_back(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def down1(ctx):
            ctx.execute("DROP TABLE t1")

        manager.register(1, "Create t1", up1, down1)

        manager.migrate_up()
        assert manager.get_current_version() == 1

        rolled_back = manager.migrate_down(target_version=0)

        assert rolled_back == [1]
        assert manager.get_current_version() == 0

    def test_migrate_down_requires_down_function(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        manager.register(1, "Create t1", up1, down=None)

        manager.migrate_up()

        with pytest.raises(MigrationError, match="no down function"):
            manager.migrate_down(target_version=0)

    def test_migrate_down_target_greater_than_current_raises(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.migrate_up()

        with pytest.raises(MigrationError, match="greater than current"):
            manager.migrate_down(target_version=5)

    def test_migrate_up_target_less_than_current_raises(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def up2(ctx):
            ctx.execute("CREATE TABLE t2 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.register(2, "Create t2", up2)
        manager.migrate_up(target_version=2)

        # Can't use migrate_up() to go backwards
        with pytest.raises(MigrationError, match="less than current"):
            manager.migrate_up(target_version=1)

    def test_migration_context_execute(self, manager):
        def up(ctx):
            ctx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            cursor = ctx.execute("INSERT INTO test VALUES (?, ?)", (1, "test"))
            result = ctx.execute("SELECT * FROM test")
            rows = result.fetchall()
            assert len(rows) == 1

        manager.register(1, "Test", up)
        manager.migrate_up()

    def test_migration_context_executemany(self, manager):
        def up(ctx):
            ctx.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            ctx.executemany("INSERT INTO test VALUES (?, ?)", [(1, "a"), (2, "b"), (3, "c")])

        manager.register(1, "Bulk insert", up)
        manager.migrate_up()

        import sqlite3

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 3
        conn.close()

    def test_migration_context_execute_script(self, manager):
        def up(ctx):
            ctx.execute_script("""
                CREATE TABLE t1 (id INTEGER);
                CREATE TABLE t2 (id INTEGER);
            """)

        manager.register(1, "Script", up)
        manager.migrate_up()

        import sqlite3

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        assert cursor.fetchone()[0] >= 3  # t1, t2, _schema_migrations
        conn.close()

    def test_migration_context_connection(self, manager):
        def up(ctx):
            conn = ctx.connection
            cursor = conn.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1

        manager.register(1, "Connection test", up)
        manager.migrate_up()

    def test_migration_failure_triggers_rollback(self, manager):
        def up(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")
            raise ValueError("Intentional failure")

        manager.register(1, "Failing migration", up)

        with pytest.raises(MigrationError, match="failed"):
            manager.migrate_up()

        assert manager.get_current_version() == 0

    def test_status_returns_correct_info(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def up2(ctx):
            ctx.execute("CREATE TABLE t2 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.register(2, "Create t2", up2)

        status = manager.status()

        assert status["current_version"] == 0
        assert status["latest_version"] == 2
        assert status["pending_count"] == 2
        assert status["applied_count"] == 0
        assert status["is_up_to_date"] is False

    def test_status_after_migrations(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.migrate_up()

        status = manager.status()

        assert status["current_version"] == 1
        assert status["pending_count"] == 0
        assert status["applied_count"] == 1
        assert status["is_up_to_date"] is True

    def test_reset_drops_migrations_table(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        manager.migrate_up()

        manager.reset()

        import sqlite3

        conn = sqlite3.connect(manager.db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='_schema_migrations'"
        )
        assert cursor.fetchone() is None
        conn.close()

    def test_migration_records_duration(self, manager):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        manager.register(1, "Create t1", up1)
        applied = manager.migrate_up()

        assert applied[0].duration_ms is not None
        assert applied[0].duration_ms >= 0


class TestCreateMigrationManager:
    """Tests for create_migration_manager factory function."""

    @pytest.fixture
    def db_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "test.db")

    def test_factory_creates_manager_with_migrations(self, db_path):
        def up1(ctx):
            ctx.execute("CREATE TABLE t1 (id INTEGER)")

        def down1(ctx):
            ctx.execute("DROP TABLE t1")

        manager = create_migration_manager(db_path, [(1, "Create t1", up1, down1)])

        assert 1 in manager._migrations
        assert manager._migrations[1].description == "Create t1"


class TestAppliedMigration:
    """Tests for AppliedMigration dataclass."""

    def test_applied_migration_creation(self):
        from dataclasses import is_dataclass

        assert is_dataclass(AppliedMigration)

        migration = AppliedMigration(
            version=1, description="Test", applied_at="2024-01-01T00:00:00", duration_ms=10.5
        )

        assert migration.version == 1
        assert migration.description == "Test"
        assert migration.applied_at == "2024-01-01T00:00:00"
        assert migration.duration_ms == 10.5


class TestMigration:
    """Tests for Migration dataclass."""

    def test_migration_creation(self):
        def up(ctx):
            pass

        migration = Migration(version=1, description="Test", up=up, down=None)

        assert migration.version == 1
        assert migration.description == "Test"
        assert migration.up is up
        assert migration.down is None
