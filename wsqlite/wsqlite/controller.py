import sqlite3
from pydantic import BaseModel, Field
from typing import Type, List, Optional, Any


class WSQLite:
    def __init__(self, model: Type[BaseModel], db_name: str):
        self.model = model
        self.db_name = db_name
        self.table_name = model.__name__.lower()

        self._create_table_if_not_exists()
        self._sync_table_with_model()

    def _get_connection(self):
        """Obtiene una conexión a la base de datos."""
        return sqlite3.connect(self.db_name)

    def _create_table_if_not_exists(self):
        """Crea la tabla en SQLite si no existe."""
        fields = ", ".join(
            f"{field} {self._get_sql_type(typ)}"
            for field, typ in self.model.model_fields.items()
        )
        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({fields})"

        with self._get_connection() as conn:
            conn.execute(query)

    def _sync_table_with_model(self):
        """Sincroniza la tabla con el modelo Pydantic, agregando nuevos campos si es necesario."""
        with self._get_connection() as conn:
            cursor = conn.execute(f"PRAGMA table_info({self.table_name})")
            existing_columns = {
                row[1] for row in cursor.fetchall()
            }  # row[1] es el nombre de la columna

        model_fields = set(self.model.model_fields.keys())
        new_fields = model_fields - existing_columns

        if new_fields:
            with self._get_connection() as conn:
                for field in new_fields:
                    field_type = self._get_sql_type(self.model.model_fields[field])
                    alter_query = f"ALTER TABLE {self.table_name} ADD COLUMN {field} {field_type} DEFAULT NULL"
                    conn.execute(alter_query)
                conn.commit()

    def _get_sql_type(self, field):
        """Convierte tipos de Pydantic a tipos de SQLite con soporte para restricciones."""
        type_mapping = {int: "INTEGER", str: "TEXT", bool: "BOOLEAN"}
        sql_type = type_mapping.get(field.annotation, "TEXT")

        constraints = []
        if "primary" in (field.description or "").lower():
            constraints.append("PRIMARY KEY")
        if "unique" in (field.description or "").lower():
            constraints.append("UNIQUE")
        if "not null" in (field.description or "").lower():
            constraints.append("NOT NULL")

        return f"{sql_type} {' '.join(constraints)}".strip()

    def insert(self, data: BaseModel):
        """Inserta un nuevo registro en la base de datos."""
        fields = ", ".join(data.model_dump().keys())
        placeholders = ", ".join(["?" for _ in data.model_dump()])
        values = tuple(data.model_dump().values())

        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        with self._get_connection() as conn:
            conn.execute(query, values)
            conn.commit()

    def get_all(self) -> List[BaseModel]:
        """Obtiene todos los registros de la tabla y maneja valores NULL."""
        query = f"SELECT * FROM {self.table_name}"

        with self._get_connection() as conn:
            cursor = conn.execute(query)
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def get_by_field(self, **filters) -> List[BaseModel]:
        """Obtiene registros filtrando por cualquier campo."""
        if not filters:
            return self.get_all()

        conditions = " AND ".join(f"{key} = ?" for key in filters.keys())
        values = tuple(filters.values())

        query = f"SELECT * FROM {self.table_name} WHERE {conditions}"

        with self._get_connection() as conn:
            cursor = conn.execute(query, values)
            rows = cursor.fetchall()

        return [
            self.model(
                **{
                    key: (value if value is not None else self._default_value(key))
                    for key, value in zip(self.model.model_fields.keys(), row)
                }
            )
            for row in rows
        ]

    def update(self, record_id: int, data: BaseModel):
        """Actualiza un registro en la base de datos."""
        fields = ", ".join(f"{key} = ?" for key in data.model_dump().keys())
        values = tuple(data.model_dump().values()) + (record_id,)

        query = f"UPDATE {self.table_name} SET {fields} WHERE id = ?"

        with self._get_connection() as conn:
            conn.execute(query, values)
            conn.commit()

    def delete(self, record_id: int):
        """Elimina un registro de la base de datos."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"

        with self._get_connection() as conn:
            conn.execute(query, (record_id,))
            conn.commit()

    def _default_value(self, field: str) -> Any:
        """Devuelve un valor por defecto si el campo es NULL en la base de datos."""
        field_type = self.model.model_fields[field].annotation
        if field_type is str:
            return ""
        elif field_type is int:
            return 0
        elif field_type is bool:
            return False
        return None
