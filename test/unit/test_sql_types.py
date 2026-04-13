"""Tests for SQL types module."""

import pytest
from pydantic import BaseModel, Field

from wsqlite.types import get_sql_type


class TestGetSqlType:
    """Tests for get_sql_type function."""

    def test_integer_type(self):
        """Test integer type mapping."""

        class Model(BaseModel):
            id: int

        field = Model.model_fields["id"]
        sql_type = get_sql_type(field)
        assert "INTEGER" in sql_type

    def test_string_type(self):
        """Test string type mapping."""

        class Model(BaseModel):
            name: str

        field = Model.model_fields["name"]
        sql_type = get_sql_type(field)
        assert "TEXT" in sql_type

    def test_boolean_type(self):
        """Test boolean type mapping."""

        class Model(BaseModel):
            active: bool

        field = Model.model_fields["active"]
        sql_type = get_sql_type(field)
        assert "INTEGER" in sql_type

    def test_primary_key_constraint(self):
        """Test primary key constraint."""

        class Model(BaseModel):
            id: int = Field(..., description="Primary Key")

        field = Model.model_fields["id"]
        sql_type = get_sql_type(field)
        assert "PRIMARY KEY" in sql_type

    def test_unique_constraint(self):
        """Test unique constraint."""

        class Model(BaseModel):
            email: str = Field(..., description="UNIQUE")

        field = Model.model_fields["email"]
        sql_type = get_sql_type(field)
        assert "UNIQUE" in sql_type

    def test_not_null_constraint(self):
        """Test not null constraint."""

        class Model(BaseModel):
            name: str = Field(..., description="NOT NULL")

        field = Model.model_fields["name"]
        sql_type = get_sql_type(field)
        assert "NOT NULL" in sql_type

    def test_multiple_constraints(self):
        """Test multiple constraints."""

        class Model(BaseModel):
            id: int = Field(..., description="Primary Key NOT NULL")
            email: str = Field(..., description="UNIQUE NOT NULL")

        id_field = Model.model_fields["id"]
        email_field = Model.model_fields["email"]

        id_type = get_sql_type(id_field)
        email_type = get_sql_type(email_field)

        assert "PRIMARY KEY" in id_type
        assert "NOT NULL" in id_type
        assert "UNIQUE" in email_type
        assert "NOT NULL" in email_type

    def test_unknown_type_defaults_to_text(self):
        """Test unknown type defaults to TEXT."""
        from typing import Optional

        class Model(BaseModel):
            data: Optional[dict]

        field = Model.model_fields["data"]
        sql_type = get_sql_type(field)
        assert "TEXT" in sql_type
