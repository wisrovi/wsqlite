"""Unit tests for WSQLite Multi-Table Manager and Dynamic Registry.

This module validates that:
1. Multiple Pydantic models can be registered in a single WSQLite instance.
2. Models can be accessed via dictionary indexing `app[User]` and attribute access `app.user`.
3. Dynamic model registration functions correctly.
"""

from typing import Optional
from pydantic import BaseModel
import pytest
from wsqlite.core.repository import WSQLite


class User(BaseModel):
    """User model for multi-table test."""

    id: Optional[int] = None
    username: str


class Product(BaseModel):
    """Product model for multi-table test."""

    id: Optional[int] = None
    title: str
    price: float


def test_multi_table_registration_and_access():
    """Verify registration and lookup of multiple models in WSQLite.

    Validates indexing via model class `app[User]`, string key `app['user']`,
    and dynamic attribute access `app.user` and `app.product`.
    """
    app = WSQLite(models=[User, Product], db_path=":memory:")
    assert app.is_multi_table is True

    # Dictionary indexing by type and name
    user_repo = app[User]
    product_repo = app["product"]

    assert user_repo.table_name == "user"
    assert product_repo.table_name == "product"

    # Attribute access
    assert app.user.table_name == "user"
    assert app.product.table_name == "product"


def test_dynamic_register_model():
    """Verify dynamic runtime registration of new models into an existing WSQLite instance.

    Validates calling register_model post-instantiation properly updates internal registries.
    """
    app = WSQLite(db_path=":memory:")
    app.register_model(User)
    app.register_model(Product)

    assert app.user.table_name == "user"
    assert app.product.table_name == "product"
