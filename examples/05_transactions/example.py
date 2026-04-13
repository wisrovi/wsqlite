import os
from pydantic import BaseModel
from wsqlite import WSQLite

DB_PATH = "example.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)


class Account(BaseModel):
    id: int
    name: str
    balance: float


db = WSQLite(Account, DB_PATH)
db.insert(Account(id=1, name="Alice", balance=1000.0))
db.insert(Account(id=2, name="Bob", balance=500.0))

print("=== BEFORE TRANSFER ===")
print(f"Alice: {db.get_by_field(id=1)[0].balance}")
print(f"Bob: {db.get_by_field(id=2)[0].balance}")

print("\n=== USING execute_transaction ===")
db.execute_transaction(
    [
        ("UPDATE account SET balance = balance - 100 WHERE id = ?", (1,)),
        ("UPDATE account SET balance = balance + 100 WHERE id = ?", (2,)),
    ]
)

print(f"Alice: {db.get_by_field(id=1)[0].balance}")
print(f"Bob: {db.get_by_field(id=2)[0].balance}")

print("\n=== USING with_transaction ===")


def transfer(txn):
    txn.execute("UPDATE account SET balance = balance - 50 WHERE id = ?", (1,))
    txn.execute("UPDATE account SET balance = balance + 50 WHERE id = ?", (2,))


db.with_transaction(transfer)

print(f"Alice: {db.get_by_field(id=1)[0].balance}")
print(f"Bob: {db.get_by_field(id=2)[0].balance}")

os.remove(DB_PATH)
print("\nDone!")
