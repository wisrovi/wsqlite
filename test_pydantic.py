import json
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    id: int
    data: dict
    items: list
    created_at: datetime
    uid: UUID

m = MyModel(id=1, data={"a": 1}, items=[1, 2], created_at=datetime.now(), uid="12345678-1234-5678-1234-567812345678")
dump = m.model_dump(mode='json')
print(dump)
print(type(dump['data']))
print(type(dump['created_at']))

# Can Pydantic reconstruct from dict with JSON strings?
try:
    m2 = MyModel(id=1, data=json.dumps({"a": 1}), items=json.dumps([1,2]), created_at=dump['created_at'], uid=dump['uid'])
    print(m2)
except Exception as e:
    print(e)
