Transactions Tutorial
======================

This tutorial covers transaction management in wsqlite.

Basic Transactions
-------------------

Using execute_transaction:

.. code-block:: python

   from pydantic import BaseModel
   from wsqlite import WSQLite

   class Account(BaseModel):
       id: int
       name: str
       balance: float

   db = WSQLite(Account, "bank.db")

   # Setup initial data
   db.insert(Account(id=1, name="Alice", balance=1000.0))
   db.insert(Account(id=2, name="Bob", balance=500.0))

   # Execute transfer transaction
   result = db.execute_transaction([
       ("UPDATE account SET balance = balance - 100 WHERE id = ?", (1,)),
       ("UPDATE account SET balance = balance + 100 WHERE id = ?", (2,)),
   ])

   # Verify transfer
   alice = db.get_by_field(id=1)[0]
   bob = db.get_by_field(id=2)[0]
   print(f"Alice: ${alice.balance}, Bob: ${bob.balance}")

Using with_transaction
---------------------

For complex operations:

.. code-block:: python

   def transfer_funds(txn, from_id, to_id, amount):
       """Transfer funds using transaction callback."""
       # Debit
       txn.execute(
           "UPDATE account SET balance = balance - ? WHERE id = ?",
           (amount, from_id)
       )
       # Credit
       txn.execute(
           "UPDATE account SET balance = balance + ? WHERE id = ?",
           (amount, to_id)
       )

   # Execute the transfer
   db.with_transaction(lambda txn: transfer_funds(txn, 1, 2, 50))

Async Transactions
-----------------

For async applications:

.. code-block:: python

   import asyncio

   async def async_transfer():
       operations = [
           ("UPDATE account SET balance = balance - ? WHERE id = ?", (25, 1)),
           ("UPDATE account SET balance = balance + ? WHERE id = ?", (25, 2)),
       ]
       await db.execute_transaction_async(operations)

   asyncio.run(async_transfer())

Transaction with Callbacks
--------------------------

Using with_transaction_async:

.. code-block:: python

   async def async_operation(txn):
       await txn.execute(
           "UPDATE account SET balance = balance - 10 WHERE id = ?",
           (1,)
       )
       await txn.execute(
           "UPDATE account SET balance = balance + 10 WHERE id = ?",
           (2,)
       )

   async def main():
       await db.with_transaction_async(async_operation)

   asyncio.run(main())