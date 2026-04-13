"""Tests for async methods."""

import asyncio
import os
import tempfile
import uuid

import pytest
from pydantic import BaseModel


class TestAsyncMethods:
    """Tests for async methods in WSQLite."""

    @pytest.mark.asyncio
    async def test_insert_async(self):
        """Test async insert."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        await db.insert_async(User(id=1, name="Alice"))

        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute("SELECT * FROM user")
            rows = await cursor.fetchall()

        assert len(rows) == 1
        assert rows[0][1] == "Alice"

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_get_all_async(self):
        """Test async get_all."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.execute("INSERT INTO user VALUES (1, 'Alice')")
            await conn.execute("INSERT INTO user VALUES (2, 'Bob')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        users = await db.get_all_async()
        assert len(users) == 2

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_get_by_field_async(self):
        """Test async get_by_field."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.execute("INSERT INTO user VALUES (1, 'Alice')")
            await conn.execute("INSERT INTO user VALUES (2, 'Bob')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        users = await db.get_by_field_async(name="Alice")
        assert len(users) == 1
        assert users[0].name == "Alice"

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_update_async(self):
        """Test async update."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.execute("INSERT INTO user VALUES (1, 'Alice')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        await db.update_async(1, User(id=1, name="Alice Updated"))

        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute("SELECT name FROM user WHERE id = 1")
            row = await cursor.fetchone()

        assert row[0] == "Alice Updated"

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_delete_async(self):
        """Test async delete."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.execute("INSERT INTO user VALUES (1, 'Alice')")
            await conn.execute("INSERT INTO user VALUES (2, 'Bob')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        await db.delete_async(1)

        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM user")
            count = await cursor.fetchone()

        assert count[0] == 1

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_get_paginated_async(self):
        """Test async get_paginated."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            for i in range(15):
                await conn.execute(f"INSERT INTO user VALUES ({i + 1}, 'User{i + 1}')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        users = await db.get_paginated_async(limit=5, offset=0)
        assert len(users) == 5

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_count_async(self):
        """Test async count."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.execute("INSERT INTO user VALUES (1, 'Alice')")
            await conn.execute("INSERT INTO user VALUES (2, 'Bob')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        count = await db.count_async()
        assert count == 2

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_insert_many_async(self):
        """Test async insert_many."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        users = [User(id=i, name=f"User{i}") for i in range(10)]
        await db.insert_many_async(users)

        count = await db.count_async()
        assert count == 10

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_delete_many_async(self):
        """Test async delete_many."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            for i in range(5):
                await conn.execute(f"INSERT INTO user VALUES ({i + 1}, 'User{i + 1}')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        await db.delete_many_async([1, 2, 3])

        count = await db.count_async()
        assert count == 2

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_get_page_async(self):
        """Test async get_page."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            for i in range(15):
                await conn.execute(f"INSERT INTO user VALUES ({i + 1}, 'User{i + 1}')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        page = await db.get_page_async(page=2, per_page=5)
        assert len(page) == 5
        assert page[0].name == "User6"

        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.mark.asyncio
    async def test_execute_transaction_async(self):
        """Test async execute_transaction."""
        import aiosqlite

        db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex[:8]}.db")

        class User(BaseModel):
            id: int
            name: str

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("CREATE TABLE user (id INTEGER, name TEXT)")
            await conn.execute("INSERT INTO user VALUES (1, 'Alice')")
            await conn.commit()

        from wsqlite import WSQLite

        db = WSQLite(User, db_path)
        await db.execute_transaction_async(
            [
                ("UPDATE user SET name = ? WHERE id = ?", ("Bob", 1)),
            ]
        )

        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute("SELECT name FROM user WHERE id = 1")
            row = await cursor.fetchone()

        assert row[0] == "Bob"

        if os.path.exists(db_path):
            os.remove(db_path)
