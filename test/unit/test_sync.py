"""Tests for table sync module."""

import asyncio
import os
import tempfile
import uuid

import pytest
from pydantic import BaseModel, Field

from wsqlite.core.sync import TableSync, AsyncTableSync, validate_identifier
from wsqlite.core.pool import close_pool
from wsqlite.exceptions import SQLInjectionError


@pytest.fixture
def db_path():
    """Unique database path for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, f"test_{uuid.uuid4().hex[:8]}.db")
    close_pool()


class TestTableSync:
    """Tests for TableSync class."""

    def test_create_if_not_exists(self, db_path):
        """Test create_if_not_exists method."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        assert os.path.exists(db_path)

    def test_table_exists_after_create(self, db_path):
        """Test table_exists method."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        assert sync.table_exists() is True

    def test_table_not_exists(self, db_path):
        """Test table_exists returns False for non-existent table."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        assert sync.table_exists() is False

    def test_get_columns(self, db_path):
        """Test get_columns method."""

        class User(BaseModel):
            id: int
            name: str
            age: int

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        columns = sync.get_columns()
        assert "id" in columns
        assert "name" in columns
        assert "age" in columns

    def test_drop_table(self, db_path):
        """Test drop_table method."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.drop_table()

        assert sync.table_exists() is False

    def test_create_index(self, db_path):
        """Test create_index method."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.create_index(["name"])

        indexes = sync.get_indexes()
        assert len(indexes) > 0

    def test_create_unique_index(self, db_path):
        """Test create_index with unique=True."""

        class User(BaseModel):
            id: int
            email: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.create_index(["email"], unique=True)

        indexes = sync.get_indexes()
        assert len(indexes) > 0

    def test_create_index_with_custom_name(self, db_path):
        """Test create_index with custom name."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.create_index(["name"], index_name="my_custom_index")

        indexes = sync.get_indexes()
        idx_names = [idx["name"] for idx in indexes]
        assert "my_custom_index" in idx_names

    def test_drop_index(self, db_path):
        """Test drop_index method."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.create_index(["name"], index_name="idx_name_test")
        sync.drop_index("idx_name_test")

        indexes = sync.get_indexes()
        idx_names = [idx["name"] for idx in indexes]
        assert "idx_name_test" not in idx_names

    def test_get_indexes(self, db_path):
        """Test get_indexes method."""

        class User(BaseModel):
            id: int
            name: str
            email: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.create_index(["name"])
        sync.create_index(["email"])

        indexes = sync.get_indexes()
        assert len(indexes) >= 2

        for idx in indexes:
            assert "name" in idx
            assert "unique" in idx
            assert "columns" in idx

    def test_sync_with_model_adds_columns(self, db_path):
        """Test sync_with_model adds new columns."""

        class UserV1(BaseModel):
            id: int
            name: str

        sync = TableSync(UserV1, db_path)
        sync.create_if_not_exists()

        class UserV2(BaseModel):
            id: int
            name: str
            age: int = Field(default=0)

        sync.model = UserV2
        sync.sync_with_model()

        columns = sync.get_columns()
        assert "age" in columns

    def test_sync_with_model_no_changes(self, db_path):
        """Test sync_with_model when no changes needed."""

        class User(BaseModel):
            id: int
            name: str

        sync = TableSync(User, db_path)
        sync.create_if_not_exists()

        sync.sync_with_model()

        columns = sync.get_columns()
        assert len(columns) == 2

    def test_sync_with_model_multiple_columns(self, db_path):
        """Test sync_with_model adds multiple new columns."""

        class UserV1(BaseModel):
            id: int

        sync = TableSync(UserV1, db_path)
        sync.create_if_not_exists()

        class UserV2(BaseModel):
            id: int
            name: str
            age: int
            email: str

        sync.model = UserV2
        sync.sync_with_model()

        columns = sync.get_columns()
        assert "name" in columns
        assert "age" in columns
        assert "email" in columns

    def test_table_name_from_model(self, db_path):
        """Test table name is derived from model name."""

        class MyUserModel(BaseModel):
            id: int

        sync = TableSync(MyUserModel, db_path)
        assert sync.table_name == "myusermodel"


class TestAsyncTableSync:
    """Tests for AsyncTableSync class."""

    def test_async_table_sync_init(self, db_path):
        """Test AsyncTableSync initialization."""

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        assert sync.model == User
        assert sync.db_path == db_path
        assert sync.table_name == "user"

    def test_async_table_sync_table_name(self, db_path):
        """Test table name from model."""

        class UserProfile(BaseModel):
            id: int

        sync = AsyncTableSync(UserProfile, db_path)
        assert sync.table_name == "userprofile"

    @pytest.mark.asyncio
    async def test_create_if_not_exists_async(self, db_path):
        """Test async create_if_not_exists."""
        import aiosqlite

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        await sync.create_if_not_exists_async()

        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='user'"
            )
            row = await cursor.fetchone()
            assert row is not None

    @pytest.mark.asyncio
    async def test_table_exists_async_true(self, db_path):
        """Test async table_exists returns True."""

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        await sync.create_if_not_exists_async()

        exists = await sync.table_exists_async()
        assert exists is True

    @pytest.mark.asyncio
    async def test_table_exists_async_false(self, db_path):
        """Test async table_exists returns False."""

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        exists = await sync.table_exists_async()
        assert exists is False

    @pytest.mark.asyncio
    async def test_drop_table_async(self, db_path):
        """Test async drop_table."""

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        await sync.create_if_not_exists_async()
        await sync.drop_table_async()

        exists = await sync.table_exists_async()
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_columns_async(self, db_path):
        """Test async get_columns."""

        class User(BaseModel):
            id: int
            name: str
            age: int

        sync = AsyncTableSync(User, db_path)
        await sync.create_if_not_exists_async()

        columns = await sync.get_columns_async()
        assert "id" in columns
        assert "name" in columns
        assert "age" in columns

    @pytest.mark.asyncio
    async def test_sync_with_model_async(self, db_path):
        """Test async sync_with_model."""

        class UserV1(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(UserV1, db_path)
        await sync.create_if_not_exists_async()

        class UserV2(BaseModel):
            id: int
            name: str
            email: str

        sync.model = UserV2
        await sync.sync_with_model_async()

        columns = await sync.get_columns_async()
        assert "email" in columns

    @pytest.mark.asyncio
    async def test_create_index_async(self, db_path):
        """Test async create_index."""

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        await sync.create_if_not_exists_async()

        await sync.create_index_async(["name"])

        exists = await sync.table_exists_async()
        assert exists is True

    @pytest.mark.asyncio
    async def test_drop_index_async(self, db_path):
        """Test async drop_index."""

        class User(BaseModel):
            id: int
            name: str

        sync = AsyncTableSync(User, db_path)
        await sync.create_if_not_exists_async()

        await sync.create_index_async(["name"], index_name="test_idx")
        await sync.drop_index_async("test_idx")


class TestValidateIdentifier:
    """Tests for validate_identifier function."""

    def test_valid_identifier(self):
        """Test valid identifiers."""
        validate_identifier("users")
        validate_identifier("my_table")
        validate_identifier("table123")
        validate_identifier("_private")
        validate_identifier("TableName")

    def test_valid_identifier_unicode(self):
        """Test identifiers with numbers."""
        validate_identifier("table1")
        validate_identifier("user_2_table")

    def test_invalid_identifier_sql_injection(self):
        """Test invalid identifiers with SQL injection attempts."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("users; DROP TABLE")

    def test_invalid_identifier_starts_with_number(self):
        """Test identifier starting with number."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("123table")

    def test_invalid_identifier_hyphen(self):
        """Test identifier with hyphen."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("my-table")

    def test_invalid_identifier_space(self):
        """Test identifier with space."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("my table")

    def test_invalid_identifier_special_chars(self):
        """Test identifier with special characters."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("user;DROP")

    def test_invalid_identifier_empty(self):
        """Test empty identifier."""
        with pytest.raises(SQLInjectionError):
            validate_identifier("")

    def test_invalid_identifier_only_underscore(self):
        """Test identifier that is only underscore."""
        validate_identifier("_")  # This should be valid
