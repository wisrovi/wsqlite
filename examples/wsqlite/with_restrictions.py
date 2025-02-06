from pydantic import BaseModel, Field
from typing import Optional
from wsqlite import WSQLite


# Definir el modelo con restricciones
class SimpleModel3(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[str] = Field(None, description="UNIQUE")  # Email debe ser único


# Crear la base de datos y sincronizar con el modelo
db = WSQLite(SimpleModel3, "database.db")

# Insertar datos válidos
db.insert(
    SimpleModel3(
        id=1, name="Juan Pérez", age=30, is_active=True, email="juan@example.com"
    )
)

# Intentar insertar un usuario con el mismo email (esto fallará)
try:
    db.insert(
        SimpleModel3(
            id=2, name="Ana López", age=25, is_active=True, email="juan@example.com"
        )
    )
except Exception as e:
    print("Error al insertar usuario duplicado:", e)

# Insertar otro usuario con un email diferente (esto funcionará)
db.insert(
    SimpleModel3(
        id=3, name="Pedro Gómez", age=40, is_active=False, email="pedro@example.com"
    )
)

# Ver datos almacenados
print("Usuarios en la base de datos:", db.get_all())
