"""Unit tests for @view decorator in WSQLite."""

import pytest
from pydantic import BaseModel
from wsqlite import WSQLite, view
from wsqlite.exceptions import OperationError


class User(BaseModel):
    id: int
    name: str


class Invoice(BaseModel):
    id: int
    user_id: int
    amount: float


@view(
    name="user_invoice_summary",
    depends_on=[User, Invoice],
    query="""
        SELECT u.id AS user_id, u.name AS user_name, SUM(i.amount) AS total_amount
        FROM user u
        LEFT JOIN invoice i ON u.id = i.user_id
        GROUP BY u.id, u.name
    """,
)
class UserInvoiceSummary(BaseModel):
    user_id: int
    user_name: str
    total_amount: float


def test_sqlite_view_creation_and_query(tmp_path):
    db_file = str(tmp_path / "test_views.db")
    db = WSQLite([User, Invoice, UserInvoiceSummary], db_file)

    db[User].insert(User(id=1, name="Alice"))
    db[Invoice].insert(Invoice(id=101, user_id=1, amount=100.0))
    db[Invoice].insert(Invoice(id=102, user_id=1, amount=50.0))

    summaries = db[UserInvoiceSummary].get_all()
    assert len(summaries) == 1
    assert summaries[0].user_name == "Alice"
    assert summaries[0].total_amount == 150.0


def test_sqlite_view_read_only_restriction(tmp_path):
    db_file = str(tmp_path / "test_views.db")
    db = WSQLite([User, Invoice, UserInvoiceSummary], db_file)

    with pytest.raises(OperationError, match="Database Views are read-only"):
        db[UserInvoiceSummary].insert(
            UserInvoiceSummary(user_id=1, user_name="Alice", total_amount=150.0)
        )
