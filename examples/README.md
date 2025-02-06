# Examples

This directory contains a collection of examples that demonstrate the usage of various modules and functionalities in this project. Each subfolder corresponds to a specific module and includes example scripts to help you understand how to use that module.

## Directory Structure

The examples are organized as follows:

```
examples/
    wsqlite/
        crupd.py
        new_columns.py
        with_restrictions.py
```

## How to Use

1. Navigate to the module folder of interest, e.g., `examples/module1/`.
2. Open the `README.md` in that folder to get detailed information about the examples.
3. Run the scripts directly using:
   ```bash
   python example1.py
   ```

## Modules and Examples

### wsqlite

#### Description
This module demonstrates specific functionalities.


- **crupd.py**: Example demonstrating functionality.
```python
from pydantic import BaseModel, Field
from wsqlite import WSQLite


# Definir el modelo sin restricciones de email
class SimpleModel2(BaseModel):
    id: int
    name: str
    age: int
    is_active: bool


# Crear la base de datos y la tabla si no existe
db = WSQLite(SimpleModel2, "database.db")

# Insertar datos
db.insert(SimpleModel2(id=1, name="Juan Pérez", age=30, is_active=True))
db.insert(SimpleModel2(id=2, name="Ana López", age=25, is_active=True))
db.insert(SimpleModel2(id=3, name="Pedro Gómez", age=40, is_active=False))

# Buscar todos los registros
print("Todos los usuarios:", db.get_all())

# Buscar por un campo específico
print("Usuarios llamados Juan:", db.get_by_field(name="Juan Pérez"))

# Buscar por múltiples filtros
print("Usuarios activos con 25 años:", db.get_by_field(age=25, is_active=True))

# Actualizar un usuario
db.update(1, SimpleModel2(id=1, name="Juan Pérez", age=31, is_active=False))
print("Usuario actualizado:", db.get_by_field(id=1))

# Eliminar un usuario
db.delete(3)
print("Usuarios después de eliminar a Pedro:", db.get_all())
  ```


- **new_columns.py**: Example demonstrating functionality.
```python
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
  ```


- **with_restrictions.py**: Example demonstrating functionality.
```python
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
  ```


