import os
from datetime import datetime
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

class Record(BaseModel):
    id: int
    data: str

db = WSQLite(Record, DB_PATH)
now = datetime.now().isoformat()
db.insert(Record(id=1, data="Test"))
record = db.get_by_field(id=1)[0]
print(f"Record: {record}")
os.remove(DB_PATH)
print("Done!")
