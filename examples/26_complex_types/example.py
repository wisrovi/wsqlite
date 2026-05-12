import os
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Este modelo demuestra todos los tipos complejos soportados
class Event(BaseModel):
    id: Optional[int] = Field(None, description="primary autoincrement")
    event_uuid: UUID
    event_date: date
    start_time: datetime
    value: Decimal = Field(max_digits=10, decimal_places=2)
    attendees: List[str]
    metadata: Dict[str, Any]

db = WSQLite(Event, DB_PATH)

# --- Crear una instancia con datos complejos ---
event_instance = Event(
    event_uuid=uuid4(),
    event_date=date(2026, 5, 12),
    start_time=datetime(2026, 5, 12, 14, 30, 0),
    value=Decimal("1234.56"),
    attendees=["Alice", "Bob", "Charlie"],
    metadata={"location": "Virtual", "platform": "Meet"}
)

print("=== INSERTANDO TIPOS COMPLEJOS ===")
print(f"  - UUID: {event_instance.event_uuid}")
print(f"  - Decimal: {event_instance.value}")
print(f"  - Datetime: {event_instance.start_time}")
db.insert(event_instance)
print("Evento guardado.")

print("")
print("=== LEYENDO Y VALIDANDO TIPOS ===")
saved_event = db.get_all()[0]

print(f"ID recuperado: {saved_event.id}")

# Verificar que los tipos se deserializan correctamente
assert isinstance(saved_event.event_uuid, UUID)
print(f"✅ UUID deserializado correctamente: {type(saved_event.event_uuid)}")

assert isinstance(saved_event.event_date, date)
print(f"✅ Date deserializado correctamente: {type(saved_event.event_date)}")

assert isinstance(saved_event.start_time, datetime)
print(f"✅ Datetime deserializado correctamente: {type(saved_event.start_time)}")

assert isinstance(saved_event.value, Decimal)
print(f"✅ Decimal deserializado correctamente: {type(saved_event.value)}")

assert isinstance(saved_event.attendees, list)
print(f"✅ List deserializado correctamente: {type(saved_event.attendees)}")

assert isinstance(saved_event.metadata, dict)
print(f"✅ Dict deserializado correctamente: {type(saved_event.metadata)}")

os.remove(DB_PATH)
print("")
print("Done!")
