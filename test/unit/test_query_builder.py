"""Tests for query builder module."""

import pytest
from unittest.mock import patch, MagicMock

from wsqlite.builders import QueryBuilder
from wsqlite.exceptions import SQLInjectionError


class TestQueryBuilder:
    """Tests for QueryBuilder class."""

    def test_init_valid_table(self):
        """Test initialization with valid table name."""
        qb = QueryBuilder("users")
        assert qb.table_name == "users"

    def test_init_invalid_table(self):
        """Test initialization with invalid table name."""
        with pytest.raises(SQLInjectionError):
            QueryBuilder("users; DROP TABLE")

    def test_where_equals(self):
        """Test where with equals operator."""
        qb = QueryBuilder("users").where("age", "=", 25)
        query, values = qb.build_select()
        assert "WHERE age = ?" in query
        assert values == (25,)

    def test_where_greater_than(self):
        """Test where with greater than operator."""
        qb = QueryBuilder("users").where("age", ">", 18)
        query, values = qb.build_select()
        assert "WHERE age > ?" in query
        assert values == (18,)

    def test_where_less_than(self):
        """Test where with less than operator."""
        qb = QueryBuilder("users").where("age", "<", 65)
        query, values = qb.build_select()
        assert "WHERE age < ?" in query
        assert values == (65,)

    def test_where_not_equals(self):
        """Test where with not equals operator."""
        qb = QueryBuilder("users").where("status", "!=", "deleted")
        query, values = qb.build_select()
        assert "WHERE status != ?" in query
        assert values == ("deleted",)

    def test_where_like(self):
        """Test where with LIKE operator."""
        qb = QueryBuilder("users").where("name", "LIKE", "John%")
        query, values = qb.build_select()
        assert "WHERE name LIKE ?" in query
        assert values == ("John%",)

    def test_where_in(self):
        """Test where with IN operator."""
        qb = QueryBuilder("users").where("id", "IN", [1, 2, 3])
        query, values = qb.build_select()
        assert "WHERE id IN (?, ?, ?)" in query
        assert values == (1, 2, 3)

    def test_where_is_null(self):
        """Test where with IS NULL operator."""
        qb = QueryBuilder("users").where("email", "IS NULL", None)
        query, values = qb.build_select()
        assert "WHERE email IS NULL" in query

    def test_where_is_not_null(self):
        """Test where with IS NOT NULL operator."""
        qb = QueryBuilder("users").where("email", "IS NOT NULL", None)
        query, values = qb.build_select()
        assert "WHERE email IS NOT NULL" in query

    def test_multiple_where(self):
        """Test multiple where conditions."""
        qb = QueryBuilder("users").where("age", ">", 18).where("city", "=", "NYC")
        query, values = qb.build_select()
        assert "WHERE age > ? AND city = ?" in query
        assert values == (18, "NYC")

    def test_where_invalid_operator(self):
        """Test where with invalid operator."""
        with pytest.raises(ValueError):
            QueryBuilder("users").where("age", "INVALID", 18)

    def test_where_in_invalid_value(self):
        """Test where with IN operator and invalid value."""
        with pytest.raises(ValueError):
            QueryBuilder("users").where("id", "IN", "not_a_list")

    def test_order_by_asc(self):
        """Test order_by ascending."""
        qb = QueryBuilder("users").order_by("name")
        query, _ = qb.build_select()
        assert "ORDER BY name ASC" in query

    def test_order_by_desc(self):
        """Test order_by descending."""
        qb = QueryBuilder("users").order_by("name", descending=True)
        query, _ = qb.build_select()
        assert "ORDER BY name DESC" in query

    def test_limit(self):
        """Test limit clause."""
        qb = QueryBuilder("users").limit(10)
        query, _ = qb.build_select()
        assert "LIMIT 10" in query

    def test_offset(self):
        """Test offset clause."""
        qb = QueryBuilder("users").offset(20)
        query, _ = qb.build_select()
        assert "OFFSET 20" in query

    def test_limit_negative(self):
        """Test limit with negative value."""
        with pytest.raises(ValueError):
            QueryBuilder("users").limit(-1)

    def test_offset_negative(self):
        """Test offset with negative value."""
        with pytest.raises(ValueError):
            QueryBuilder("users").offset(-1)

    def test_build_count(self):
        """Test build_count method."""
        qb = QueryBuilder("users").where("age", ">", 18)
        query, values = qb.build_count()
        assert "SELECT COUNT(*) FROM users" in query
        assert "WHERE age > ?" in query
        assert values == (18,)

    def test_build_delete(self):
        """Test build_delete method."""
        qb = QueryBuilder("users").where("id", "=", 1)
        query, values = qb.build_delete()
        assert "DELETE FROM users" in query
        assert "WHERE id = ?" in query

    def test_build_delete_without_where(self):
        """Test build_delete without WHERE clause."""
        with pytest.raises(ValueError):
            QueryBuilder("users").build_delete()

    def test_reset(self):
        """Test reset method."""
        qb = QueryBuilder("users").where("age", ">", 18).order_by("name").limit(10)
        qb.reset()
        query, values = qb.build_select()
        assert "WHERE" not in query
        assert "ORDER BY" not in query
        assert "LIMIT" not in query
        assert values == ()
