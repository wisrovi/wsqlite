from pydantic import BaseModel, Field
from typing import Optional
from wsqlite import WSQLite


class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool


db = WSQLite(SimpleModel4, "database.db")  # Esto creará la tabla
# Insertar un nuevo usuario con el nuevo campo
db.insert(SimpleModel4(id=1, name="Ana López", age=25, is_active=True))


# === AHORA AÑADIMOS UN NUEVO CAMPO AL MODELO ===
class SimpleModel4(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    age: int
    is_active: bool
    email: Optional[
        str
    ]  # nuevos campos no pueden tener restricciones en la base de datos (Field)


# Crear una nueva instancia con el modelo actualizado
db = WSQLite(SimpleModel4, "database.db")  # Esto actualizará la tabla

# Insertar un nuevo usuario con el nuevo campo
db.insert(
    SimpleModel4(
        id=2, name="Ana López", age=25, is_active=True, email="ana@example.com"
    )
)

# Mostrar los datos después de la actualización
print("Usuarios después de actualizar el modelo:", db.get_all())
