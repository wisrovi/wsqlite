"""Tests for repository module."""

import os
import tempfile
import uuid

import pytest
from pydantic import BaseModel

from wsqlite import WSQLite
from wsqlite.exceptions import SQLInjectionError
from wsqlite.core.pool import close_pool


@pytest.fixture
def db_path():
    """Unique database path for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, f"test_{uuid.uuid4().hex[:8]}.db")
    close_pool()


class TestWSQLite:
    """Tests for WSQLite class."""

    def test_init_creates_table(self, db_path):
        """Test initialization creates table."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        assert os.path.exists(db_path)

    def test_insert(self, db_path):
        """Test insert method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))

        users = db.get_all()
        assert len(users) == 1
        assert users[0].name == "Alice"

    def test_get_all(self, db_path):
        """Test get_all method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))
        db.insert(User(id=2, name="Bob"))

        users = db.get_all()
        assert len(users) == 2

    def test_get_by_field(self, db_path):
        """Test get_by_field method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))
        db.insert(User(id=2, name="Bob"))

        users = db.get_by_field(name="Alice")
        assert len(users) == 1
        assert users[0].name == "Alice"

    def test_update(self, db_path):
        """Test update method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))

        db.update(1, User(id=1, name="Alice Updated"))

        users = db.get_by_field(id=1)
        assert users[0].name == "Alice Updated"

    def test_delete(self, db_path):
        """Test delete method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))
        db.insert(User(id=2, name="Bob"))

        db.delete(1)

        users = db.get_all()
        assert len(users) == 1

    def test_get_paginated(self, db_path):
        """Test get_paginated method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        for i in range(15):
            db.insert(User(id=i + 1, name=f"User{i + 1}"))

        users = db.get_paginated(limit=5, offset=0)
        assert len(users) == 5

    def test_get_page(self, db_path):
        """Test get_page method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        for i in range(15):
            db.insert(User(id=i + 1, name=f"User{i + 1}"))

        page = db.get_page(page=2, per_page=5)
        assert len(page) == 5
        assert page[0].name == "User6"

    def test_count(self, db_path):
        """Test count method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))
        db.insert(User(id=2, name="Bob"))

        count = db.count()
        assert count == 2

    def test_insert_many(self, db_path):
        """Test insert_many method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        users = [User(id=i, name=f"User{i}") for i in range(10)]
        db.insert_many(users)

        count = db.count()
        assert count == 10

    def test_update_many(self, db_path):
        """Test update_many method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        for i in range(3):
            db.insert(User(id=i + 1, name=f"User{i + 1}"))

        updates = [
            (User(id=1, name="Updated1"), 1),
            (User(id=2, name="Updated2"), 2),
        ]
        db.update_many(updates)

        users = db.get_all()
        assert users[0].name == "Updated1"
        assert users[1].name == "Updated2"

    def test_delete_many(self, db_path):
        """Test delete_many method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        for i in range(5):
            db.insert(User(id=i + 1, name=f"User{i + 1}"))

        db.delete_many([1, 2, 3])

        count = db.count()
        assert count == 2

    def test_execute_transaction(self, db_path):
        """Test execute_transaction method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))

        db.execute_transaction(
            [
                ("UPDATE user SET name = ? WHERE id = ?", ("Bob", 1)),
            ]
        )

        users = db.get_by_field(id=1)
        assert users[0].name == "Bob"

    def test_with_transaction(self, db_path):
        """Test with_transaction method."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))

        def update_user(txn=None):
            db.update(1, User(id=1, name="Updated"))

        db.with_transaction(update_user)

        users = db.get_by_field(id=1)
        assert users[0].name == "Updated"

    def test_null_default_values(self, db_path):
        """Test that null values get default values."""

        class User(BaseModel):
            id: int
            name: str
            email: str | None = None

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))

        users = db.get_all()
        assert users[0].email is None or users[0].email == ""

    def test_sql_injection_validation(self, db_path):
        """Test SQL injection prevention in field values."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))

        users = db.get_by_field(name="' OR '1'='1")
        assert len(users) == 0

    def test_get_by_field_empty_filters(self, db_path):
        """Test get_by_field with empty filters returns all records."""

        class User(BaseModel):
            id: int
            name: str

        db = WSQLite(User, db_path)
        db.insert(User(id=1, name="Alice"))
        db.insert(User(id=2, name="Bob"))

        users = db.get_by_field()
        assert len(users) == 2
