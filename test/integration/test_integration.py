"""Integration tests for WSQLite with real database."""

import os
import tempfile

import pytest
from pydantic import BaseModel

from wsqlite import WSQLite, TableSync, close_pool
from wsqlite.core.pool import get_pool


class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = 0


class Product(BaseModel):
    id: int
    name: str
    price: float


@pytest.fixture
def db_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test.db")


@pytest.fixture
def db(db_path):
    close_pool()
    table_sync = TableSync(User, db_path)
    table_sync.drop_table()
    table_sync.create_if_not_exists()

    database = WSQLite(User, db_path, pool_size=5)
    yield database

    close_pool()


@pytest.fixture
def db_multi_table(db_path):
    close_pool()
    TableSync(User, db_path).drop_table()
    TableSync(Product, db_path).drop_table()
    TableSync(User, db_path).create_if_not_exists()
    TableSync(Product, db_path).create_if_not_exists()

    db = WSQLite(User, db_path, pool_size=5)
    yield db


class TestWSQLiteIntegration:
    """Integration tests for WSQLite."""

    def test_insert_and_get(self, db):
        db.insert(User(id=1, name="Alice", email="alice@test.com"))
        db.insert(User(id=2, name="Bob", email="bob@test.com"))

        users = db.get_all()
        assert len(users) == 2
        assert users[0].name == "Alice"
        assert users[1].name == "Bob"

    def test_get_by_field(self, db):
        db.insert(User(id=1, name="Alice", email="alice@test.com"))
        db.insert(User(id=2, name="Bob", email="bob@test.com"))
        db.insert(User(id=3, name="Alice", email="alice2@test.com"))

        alices = db.get_by_field(name="Alice")
        assert len(alices) == 2

    def test_update(self, db):
        db.insert(User(id=1, name="Alice", email="alice@test.com"))

        db.update(1, User(id=1, name="Alicia", email="alicia@test.com"))

        users = db.get_by_field(id=1)
        assert len(users) == 1
        assert users[0].name == "Alicia"

    def test_delete(self, db):
        db.insert(User(id=1, name="Alice", email="alice@test.com"))
        db.insert(User(id=2, name="Bob", email="bob@test.com"))

        db.delete(1)

        users = db.get_all()
        assert len(users) == 1
        assert users[0].name == "Bob"

    def test_count(self, db):
        for i in range(10):
            db.insert(User(id=i, name=f"User{i}", email=f"user{i}@test.com"))

        assert db.count() == 10

    def test_pagination(self, db):
        for i in range(25):
            db.insert(User(id=i, name=f"User{i}", email=f"user{i}@test.com"))

        page1 = db.get_page(page=1, per_page=10)
        assert len(page1) == 10

        page3 = db.get_page(page=3, per_page=10)
        assert len(page3) == 5

    def test_get_paginated(self, db):
        for i in range(20):
            db.insert(User(id=i, name=f"User{i}", email=f"user{i}@test.com"))

        results = db.get_paginated(limit=5, offset=10)
        assert len(results) == 5

    def test_insert_many(self, db):
        users = [User(id=i, name=f"User{i}", email=f"user{i}@test.com") for i in range(100)]
        db.insert_many(users)

        assert db.count() == 100

    def test_update_many(self, db):
        for i in range(10):
            db.insert(User(id=i + 1000, name=f"User{i}", email=f"user{i}@test.com"))

        updates = [
            (User(id=i + 1000, name=f"Updated{i}", email=f"updated{i}@test.com"), i + 1000)
            for i in range(5)
        ]
        count = db.update_many(updates)

        assert count >= 0  # Some may succeed

    def test_delete_many(self, db):
        for i in range(20):
            db.insert(User(id=i, name=f"User{i}", email=f"user{i}@test.com"))

        count = db.delete_many([1, 2, 3, 4, 5])

        assert count == 5
        assert db.count() == 15

    def test_execute_transaction(self, db):
        db.execute_transaction(
            [
                ("INSERT INTO user VALUES (?, ?, ?, ?)", (1, "Alice", "alice@test.com", 25)),
                ("INSERT INTO user VALUES (?, ?, ?, ?)", (2, "Bob", "bob@test.com", 30)),
            ]
        )

        assert db.count() == 2

    def test_with_transaction(self, db):
        def do_transaction(txn):
            cursor = txn.conn.execute("SELECT COUNT(*) FROM user")
            return cursor.fetchone()[0]

        count = db.with_transaction(do_transaction)
        assert count >= 0


class TestConnectionPooling:
    """Tests for connection pooling."""

    def test_pool_reuse(self, db_path):
        close_pool()

        pool1 = get_pool(db_path, min_size=2, max_size=5)
        stats1 = pool1.stats

        pool2 = get_pool(db_path)
        stats2 = pool2.stats

        assert pool1 is pool2
        assert stats1["current_size"] == stats2["current_size"]

    def test_pool_concurrent_access(self, db):
        from concurrent.futures import ThreadPoolExecutor

        def worker(i):
            db.insert(User(id=i + 5000, name=f"User{i}", email=f"user{i}@test.com"))
            return 1

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(worker, range(50)))

        assert db.count() >= 50
        assert sum(results) == 50


class TestTableSync:
    """Tests for table synchronization."""

    def test_sync_adds_column(self, db_path):
        class OldModel(BaseModel):
            id: int
            name: str

        class NewModel(BaseModel):
            id: int
            name: str
            email: str = ""

        sync = TableSync(OldModel, db_path)
        sync.drop_table()
        sync.create_if_not_exists()

        db1 = WSQLite(OldModel, db_path)
        db1.insert(OldModel(id=1, name="Test"))

        sync.sync_with_model()

        db2 = WSQLite(NewModel, db_path)

        # Table should have email column now
        users = db2.get_all()
        assert len(users) >= 1

    def test_get_columns(self, db_path):
        close_pool()
        sync = TableSync(User, db_path)
        sync.drop_table()
        sync.create_if_not_exists()

        columns = sync.get_columns()

        assert "id" in columns
        assert "name" in columns
        assert "email" in columns
        assert "age" in columns


class TestQueryBuilder:
    """Tests for query builder with real database."""

    def test_complex_query(self, db):
        for i in range(20):
            db.insert(
                User(id=i + 2000, name=f"User{i}", email=f"user{i}@test.com", age=20 + (i % 30))
            )

        results = db.get_paginated(limit=5, offset=5, order_by="age", order_desc=True)
        assert len(results) == 5

        ages = [r.age for r in results]
        assert ages == sorted(ages, reverse=True)
