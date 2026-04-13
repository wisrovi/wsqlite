"""Tests for advanced query builder."""

import pytest

from wsqlite.builders.advanced_query_builder import (
    QueryBuilder,
    validate_field,
)
from wsqlite.exceptions import SQLInjectionError


class TestAdvancedQueryBuilder:
    """Tests for AdvancedQueryBuilder class."""

    def test_basic_select(self):
        query, params = QueryBuilder("users").build_select()
        assert "SELECT * FROM users" == query
        assert params == ()

    def test_select_specific_fields(self):
        query, params = QueryBuilder("users").select("id", "name", "email").build_select()
        assert "SELECT id, name, email FROM users" == query

    def test_select_with_alias(self):
        query, params = (
            QueryBuilder("users").select("name").select_as("COUNT(*)", "total").build_select()
        )
        assert "COUNT(*) AS total" in query
        assert "name" in query

    def test_aggregate_functions(self):
        query, _ = (
            QueryBuilder("users")
            .select_count("*", "count")
            .select_sum("balance", "total_balance")
            .select_avg("age", "avg_age")
            .select_min("age", "min_age")
            .select_max("age", "max_age")
            .build_select()
        )
        assert "COUNT(*) AS count" in query
        assert "SUM(balance) AS total_balance" in query
        assert "AVG(age) AS avg_age" in query
        assert "MIN(age) AS min_age" in query
        assert "MAX(age) AS max_age" in query

    def test_where_single_condition(self):
        query, params = QueryBuilder("users").where("age", ">=", 18).build_select()
        assert "WHERE age >= ?" in query
        assert params == (18,)

    def test_where_multiple_conditions_and(self):
        query, params = (
            QueryBuilder("users")
            .where("age", ">=", 18)
            .where("status", "=", "active")
            .build_select()
        )
        assert "WHERE age >= ?" in query
        assert "AND status = ?" in query
        assert params == (18, "active")

    def test_or_where(self):
        query, params = (
            QueryBuilder("users")
            .where("status", "=", "active")
            .or_where("role", "=", "admin")
            .build_select()
        )
        assert "WHERE status = ?" in query
        assert "OR role = ?" in query

    def test_where_in(self):
        query, params = QueryBuilder("users").where_in("id", [1, 2, 3]).build_select()
        assert "WHERE id IN (?, ?, ?)" in query
        assert params == (1, 2, 3)

    def test_where_not_in(self):
        query, params = (
            QueryBuilder("users").where_not_in("status", ["banned", "deleted"]).build_select()
        )
        assert "WHERE status NOT IN (?, ?)" in query
        assert params == ("banned", "deleted")

    def test_where_null(self):
        query, params = QueryBuilder("users").where_null("deleted_at").build_select()
        assert "deleted_at IS NULL" in query

    def test_where_not_null(self):
        query, params = QueryBuilder("users").where_not_null("email").build_select()
        assert "email IS NOT NULL" in query

    def test_where_between(self):
        query, params = QueryBuilder("users").where_between("age", 18, 65).build_select()
        assert "WHERE age BETWEEN ? AND ?" in query
        assert params == (18, 65)

    def test_where_like(self):
        query, params = QueryBuilder("users").where_like("name", "%john%").build_select()
        assert "WHERE name LIKE ?" in query
        assert params == ("%john%",)

    def test_inner_join(self):
        query, params = (
            QueryBuilder("users")
            .select("*")
            .inner_join("orders", "users.id = orders.user_id")
            .build_select()
        )
        assert "INNER JOIN orders ON users.id = orders.user_id" in query

    def test_left_join(self):
        query, params = (
            QueryBuilder("users")
            .select("*")
            .left_join("orders", "users.id = orders.user_id")
            .build_select()
        )
        assert "LEFT JOIN orders ON users.id = orders.user_id" in query

    def test_right_join(self):
        query, params = (
            QueryBuilder("users").right_join("orders", "users.id = orders.user_id").build_select()
        )
        assert "RIGHT JOIN orders ON users.id = orders.user_id" in query

    def test_join_methods(self):
        q = QueryBuilder("a")
        q.join("b", "a.id = b.id", "INNER")
        q.inner_join("c", "a.id = c.id")
        q.left_join("d", "a.id = d.id")
        q.right_join("e", "a.id = e.id")
        q.cross_join("f")
        query, _ = q.build_select()
        assert "INNER JOIN b" in query
        assert "INNER JOIN c" in query
        assert "LEFT JOIN d" in query
        assert "RIGHT JOIN e" in query
        assert "CROSS JOIN f" in query

    def test_invalid_join_type(self):
        with pytest.raises(ValueError, match="Invalid JOIN type"):
            QueryBuilder("users").join("orders", "a=b", "INVALID")

    def test_group_by(self):
        query, params = (
            QueryBuilder("orders")
            .select("user_id")
            .select_count("*", "count")
            .group_by("user_id")
            .build_select()
        )
        assert "GROUP BY user_id" in query

    def test_having(self):
        query, params = (
            QueryBuilder("orders")
            .select("user_id")
            .select_count("*", "count")
            .group_by("user_id")
            .having("COUNT(*)", ">", 10)
            .build_select()
        )
        assert "HAVING COUNT(*) > ?" in query
        assert params == (10,)

    def test_order_by_asc(self):
        query, params = QueryBuilder("users").order_by_asc("name").build_select()
        assert "ORDER BY name ASC" in query

    def test_order_by_desc(self):
        query, params = QueryBuilder("users").order_by_desc("created_at").build_select()
        assert "ORDER BY created_at DESC" in query

    def test_order_by_with_direction(self):
        query, _ = QueryBuilder("users").order_by("name", "DESC").build_select()
        assert "ORDER BY name DESC" in query

    def test_invalid_order_direction(self):
        with pytest.raises(ValueError, match="ASC or DESC"):
            QueryBuilder("users").order_by("name", "INVALID")

    def test_limit(self):
        query, params = QueryBuilder("users").limit(100).build_select()
        assert "LIMIT 100" in query

    def test_offset(self):
        query, params = QueryBuilder("users").offset(50).build_select()
        assert "OFFSET 50" in query

    def test_page_pagination(self):
        query, params = (
            QueryBuilder("users")
            .page(3, 25)  # Page 3, 25 per page = offset 50
            .build_select()
        )
        assert "LIMIT 25" in query
        assert "OFFSET 50" in query

    def test_page_with_invalid_page(self):
        query, _ = (
            QueryBuilder("users")
            .page(0, 10)  # Should become page 1
            .build_select()
        )
        assert "LIMIT 10" in query
        assert "OFFSET 0" in query

    def test_for_update(self):
        query, params = QueryBuilder("users").where("id", "=", 1).for_update().build_select()
        assert "FOR UPDATE" in query

    def test_complex_query(self):
        query, params = (
            QueryBuilder("users")
            .select("name")
            .select_count("orders.id", "order_count")
            .select_sum("orders.total", "total_spent")
            .left_join("orders", "users.id = orders.user_id")
            .where("status", "=", "active")
            .where("age", ">=", 18)
            .or_where("role", "=", "premium")
            .group_by("users.id")
            .having("COUNT(orders.id)", ">", 0)
            .order_by("total_spent", "DESC")
            .limit(10)
            .build_select()
        )
        assert "SELECT" in query
        assert "FROM users" in query
        assert "LEFT JOIN orders" in query
        assert "WHERE" in query
        assert "GROUP BY" in query
        assert "HAVING" in query
        assert "ORDER BY" in query
        assert "LIMIT 10" in query
        assert len(params) > 0

    def test_build_count(self):
        query, params = QueryBuilder("users").where("status", "=", "active").build_count()
        assert "SELECT COUNT(*)" in query
        assert "FROM users" in query
        assert "WHERE" in query

    def test_build_insert(self):
        query, params = QueryBuilder("users").build_insert(
            {"id": 1, "name": "John", "email": "john@example.com"}
        )
        assert "INSERT INTO users" in query
        assert "(id, name, email)" in query
        assert "VALUES (?, ?, ?)" in query
        assert params == (1, "John", "john@example.com")

    def test_build_update(self):
        query, params = QueryBuilder("users").build_update(
            {"name": "Jane", "email": "jane@example.com"}, "id", 1
        )
        assert "UPDATE users SET" in query
        assert "name = ?" in query
        assert "email = ?" in query
        assert "WHERE id = ?" in query
        assert params == ("Jane", "jane@example.com", 1)

    def test_build_delete(self):
        query, params = QueryBuilder("users").where("id", "=", 1).build_delete()
        assert "DELETE FROM users" in query
        assert "WHERE id = ?" in query

    def test_build_delete_requires_where(self):
        with pytest.raises(ValueError, match="requires WHERE"):
            QueryBuilder("users").build_delete()

    def test_reset_clears_builder(self):
        q = (
            QueryBuilder("users")
            .select("id", "name")
            .where("status", "=", "active")
            .order_by("name")
            .limit(10)
        )
        q.reset()
        query, _ = q.build_select()
        assert query == "SELECT * FROM users"
        assert "WHERE" not in query
        assert "ORDER BY" not in query

    def test_validate_identifier_rejects_sql_injection(self):
        with pytest.raises(SQLInjectionError):
            QueryBuilder("users; DROP TABLE users;--")

    def test_validate_field_with_table_prefix(self):
        result = validate_field("users.id")
        assert result == "users.id"

    def test_validate_field_with_star(self):
        result = validate_field("*")
        assert result == "*"

    def test_validate_field_with_function(self):
        result = validate_field("COUNT(*)")
        assert result == "COUNT(*)"

    def test_validate_field_rejects_invalid(self):
        with pytest.raises(SQLInjectionError):
            validate_field("id; DROP TABLE")

    def test_invalid_operator(self):
        with pytest.raises(ValueError, match="Invalid operator"):
            QueryBuilder("users").where("id", "INVALID", 1)

    def test_where_in_requires_list(self):
        with pytest.raises(ValueError, match="requires a list or tuple"):
            QueryBuilder("users").where("id", "IN", "not a list")

    def test_where_between_requires_list(self):
        with pytest.raises(ValueError, match="BETWEEN requires"):
            QueryBuilder("users").where("age", "BETWEEN", "not two values")
