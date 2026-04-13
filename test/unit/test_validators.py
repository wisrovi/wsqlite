"""Tests for validators module."""

from datetime import datetime, date, time
from decimal import Decimal
from typing import List, Dict, Optional, Union
from uuid import UUID

import pytest

from wsqlite.validators import (
    infer_sqlite_type,
    get_default_value,
    validate_value,
    serialize_value,
    deserialize_value,
    FieldValidator,
    SQLITE_TYPE_MAP,
    DEFAULT_VALUES,
)


class TestInferSqliteType:
    """Tests for infer_sqlite_type function."""

    def test_integer_maps_to_integer(self):
        assert infer_sqlite_type(int) == "INTEGER"

    def test_string_maps_to_text(self):
        assert infer_sqlite_type(str) == "TEXT"

    def test_float_maps_to_real(self):
        assert infer_sqlite_type(float) == "REAL"

    def test_bool_maps_to_integer(self):
        assert infer_sqlite_type(bool) == "INTEGER"

    def test_bytes_maps_to_blob(self):
        assert infer_sqlite_type(bytes) == "BLOB"

    def test_datetime_maps_to_text(self):
        assert infer_sqlite_type(datetime) == "TEXT"

    def test_date_maps_to_text(self):
        assert infer_sqlite_type(date) == "TEXT"

    def test_time_maps_to_text(self):
        assert infer_sqlite_type(time) == "TEXT"

    def test_uuid_maps_to_text(self):
        assert infer_sqlite_type(UUID) == "TEXT"

    def test_decimal_maps_to_real(self):
        assert infer_sqlite_type(Decimal) == "REAL"

    def test_list_maps_to_text(self):
        assert infer_sqlite_type(List[int]) == "TEXT"

    def test_dict_maps_to_text(self):
        assert infer_sqlite_type(Dict) == "TEXT"

    def test_unknown_defaults_to_text(self):
        assert infer_sqlite_type(object) == "TEXT"


class TestGetDefaultValue:
    """Tests for get_default_value function."""

    def test_int_default(self):
        assert get_default_value(int) == 0

    def test_str_default(self):
        assert get_default_value(str) == ""

    def test_float_default(self):
        assert get_default_value(float) == 0.0

    def test_bool_default(self):
        assert get_default_value(bool) is False

    def test_bytes_default(self):
        assert get_default_value(bytes) == b""

    def test_list_default(self):
        assert get_default_value(list) == []

    def test_dict_default(self):
        assert get_default_value(dict) == {}

    def test_datetime_default(self):
        result = get_default_value(datetime)
        assert isinstance(result, datetime)
        assert result.year == 1970

    def test_date_default(self):
        result = get_default_value(date)
        assert isinstance(result, date)
        assert result.year == 1970

    def test_time_default(self):
        result = get_default_value(time)
        assert isinstance(result, time)

    def test_uuid_default(self):
        result = get_default_value(UUID)
        assert isinstance(result, UUID)
        assert str(result) == "00000000-0000-0000-0000-000000000000"

    def test_decimal_default(self):
        result = get_default_value(Decimal)
        assert isinstance(result, Decimal)

    def test_optional_returns_str_default(self):
        result = get_default_value(Optional[str])
        assert result == ""  # Returns str default for Union[str, None]

    def test_union_returns_first_valid(self):
        result = get_default_value(Union[str, int])
        assert result == ""

    def test_unknown_returns_none(self):
        assert get_default_value(object) is None


class TestValidateValue:
    """Tests for validate_value function."""

    def test_none_returns_default(self):
        result = validate_value(int, None)
        assert result == 0

    def test_bool_from_string_true(self):
        assert validate_value(bool, "true") is True
        assert validate_value(bool, "1") is True
        assert validate_value(bool, "yes") is True

    def test_bool_from_string_false(self):
        assert validate_value(bool, "false") is False
        assert validate_value(bool, "0") is False
        assert validate_value(bool, "no") is False

    def test_int_conversion(self):
        assert validate_value(int, 5) == 5
        assert validate_value(int, "5") == 5
        assert validate_value(int, 5.9) == 5

    def test_float_conversion(self):
        assert validate_value(float, 5.5) == 5.5
        assert validate_value(float, "5.5") == 5.5
        assert validate_value(float, 5) == 5.0

    def test_str_conversion(self):
        assert validate_value(str, 123) == "123"
        assert validate_value(str, "hello") == "hello"

    def test_datetime_from_string(self):
        result = validate_value(datetime, "2024-01-15T10:30:00")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_date_from_string(self):
        result = validate_value(date, "2024-01-15")
        assert isinstance(result, date)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_time_from_string(self):
        result = validate_value(time, "10:30:00")
        assert isinstance(result, time)
        assert result.hour == 10
        assert result.minute == 30

    def test_uuid_from_string(self):
        test_uuid = "12345678-1234-1234-1234-123456789abc"
        result = validate_value(UUID, test_uuid)
        assert isinstance(result, UUID)
        assert str(result) == test_uuid

    def test_list_from_json_string(self):
        result = validate_value(List[int], "[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_dict_from_json_string(self):
        result = validate_value(Dict, '{"key": "value"}')
        assert result == {"key": "value"}

    def test_preserves_valid_value(self):
        test_dt = datetime(2024, 1, 15, 10, 30, 0)
        result = validate_value(datetime, test_dt)
        assert result == test_dt


class TestSerializeValue:
    """Tests for serialize_value function."""

    def test_bool_serialize(self):
        assert serialize_value(True, bool) == 1
        assert serialize_value(False, bool) == 0

    def test_datetime_serialize(self):
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = serialize_value(dt, datetime)
        assert result == "2024-01-15T10:30:00"

    def test_date_serialize(self):
        d = date(2024, 1, 15)
        result = serialize_value(d, date)
        assert result == "2024-01-15"

    def test_time_serialize(self):
        t = time(10, 30, 0)
        result = serialize_value(t, time)
        assert result == "10:30:00"

    def test_uuid_serialize(self):
        test_uuid = UUID("12345678-1234-1234-1234-123456789abc")
        result = serialize_value(test_uuid, UUID)
        assert result == "12345678-1234-1234-1234-123456789abc"

    def test_list_serialize(self):
        result = serialize_value([1, 2, 3], list)
        assert result == "[1, 2, 3]"

    def test_dict_serialize(self):
        result = serialize_value({"key": "value"}, dict)
        assert result == '{"key": "value"}'

    def test_none_returns_none(self):
        assert serialize_value(None, int) is None

    def test_preserves_primitives(self):
        assert serialize_value(123, int) == 123
        assert serialize_value("hello", str) == "hello"


class TestDeserializeValue:
    """Tests for deserialize_value function."""

    def test_none_returns_default(self):
        result = deserialize_value(None, int)
        assert result == 0

    def test_int_deserialize(self):
        assert deserialize_value(5, int) == 5

    def test_str_deserialize(self):
        assert deserialize_value("hello", str) == "hello"

    def test_datetime_deserialize(self):
        result = deserialize_value("2024-01-15T10:30:00", datetime)
        assert isinstance(result, datetime)


class TestFieldValidator:
    """Tests for FieldValidator class."""

    @pytest.fixture
    def sample_model(self):
        from pydantic import BaseModel

        class SampleModel(BaseModel):
            id: int
            name: str
            email: Optional[str] = None
            age: int = 25
            balance: float = 0.0
            active: bool = True

        return SampleModel

    def test_init_extracts_fields(self, sample_model):
        validator = FieldValidator(sample_model)
        assert "id" in validator._fields
        assert "name" in validator._fields
        assert "email" in validator._fields

    def test_clean_serializes_data(self, sample_model):
        validator = FieldValidator(sample_model)
        result = validator.clean({"id": 1, "name": "test", "active": True})
        assert result["id"] == 1
        assert result["name"] == "test"
        assert result["active"] == 1  # Bool to int

    def test_is_valid_type_with_valid_value(self, sample_model):
        validator = FieldValidator(sample_model)
        assert validator.is_valid_type("id", 1) is True
        assert validator.is_valid_type("name", "test") is True
        assert validator.is_valid_type("active", True) is True

    def test_is_valid_type_unknown_field(self, sample_model):
        validator = FieldValidator(sample_model)
        assert validator.is_valid_type("unknown_field", "value") is True

    def test_get_sql_type(self, sample_model):
        validator = FieldValidator(sample_model)
        assert validator.get_sql_type("id") == "INTEGER"
        assert validator.get_sql_type("name") == "TEXT"
        assert validator.get_sql_type("balance") == "REAL"
        assert validator.get_sql_type("active") == "INTEGER"

    def test_get_sql_type_unknown_field(self, sample_model):
        validator = FieldValidator(sample_model)
        assert validator.get_sql_type("unknown") == "TEXT"
