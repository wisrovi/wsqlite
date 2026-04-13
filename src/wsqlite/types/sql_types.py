"""SQL type mapping from Pydantic to SQLite."""

from typing import Any


def get_sql_type(field: Any) -> str:
    """Convert Pydantic field type to SQLite type.

    Maps Pydantic types to SQLite types:
    - int -> INTEGER
    - str -> TEXT
    - bool -> INTEGER (SQLite uses 0/1)

    Supports constraints via field description:
    - "primary" -> PRIMARY KEY
    - "unique" -> UNIQUE
    - "not null" -> NOT NULL
    """
    type_mapping = {int: "INTEGER", str: "TEXT", bool: "INTEGER"}
    sql_type = type_mapping.get(field.annotation, "TEXT")

    constraints = []
    description = (field.description or "").lower()
    if "primary" in description:
        constraints.append("PRIMARY KEY")
    if "unique" in description:
        constraints.append("UNIQUE")
    if "not null" in description:
        constraints.append("NOT NULL")

    return f"{sql_type} {' '.join(constraints)}".strip()
