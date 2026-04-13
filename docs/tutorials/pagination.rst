Pagination Tutorial
=====================

This tutorial covers different pagination strategies available in wsqlite.

Basic Pagination
----------------

Using limit and offset:

.. code-block:: python

   from wsqlite import WSQLite
   from pydantic import BaseModel

   class User(BaseModel):
       id: int
       name: str

   db = WSQLite(User, "database.db")

   # Insert test data
   for i in range(25):
       db.insert(User(id=i+1, name=f"User{i+1}"))

   # Get first 5 users
   page1 = db.get_paginated(limit=5, offset=0)
   print("Page 1:", [u.name for u in page1])

   # Get next 5 users
   page2 = db.get_paginated(limit=5, offset=5)
   print("Page 2:", [u.name for u in page2])

Page Number Pagination
---------------------

Using page numbers:

.. code-block:: python

   # Get page 1 with 10 items per page
   page1 = db.get_page(page=1, per_page=10)
   print("Page 1:", [u.name for u in page1])

   # Get page 3
   page3 = db.get_page(page=3, per_page=10)
   print("Page 3:", [u.name for u in page3])

Ordered Pagination
------------------

Add ordering to pagination:

.. code-block:: python

   # Order by name ascending
   ascending = db.get_paginated(limit=5, order_by="name", order_desc=False)
   print("Ascending:", [u.name for u in ascending])

   # Order by name descending
   descending = db.get_paginated(limit=5, order_by="name", order_desc=True)
   print("Descending:", [u.name for u in descending])

Counting Records
----------------

Get total count for pagination UI:

.. code-block:: python

   total = db.count()
   per_page = 10
   total_pages = (total + per_page - 1) // per_page

   print(f"Total records: {total}")
   print(f"Total pages: {total_pages}")

   for page in range(1, total_pages + 1):
       records = db.get_page(page=page, per_page=per_page)
       print(f"Page {page}: {len(records)} records")

Async Pagination
-----------------

For async applications:

.. code-block:: python

   import asyncio

   async def paginate_async():
       page1 = await db.get_paginated_async(limit=5, offset=0)
       print("Async page 1:", [u.name for u in page1])

       page = await db.get_page_async(page=2, per_page=10)
       print("Async page 2:", [u.name for u in page])

       count = await db.count_async()
       print(f"Total async count: {count}")

   asyncio.run(paginate_async())