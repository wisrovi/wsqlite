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
