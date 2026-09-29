"""
Lesson 2 - Pydantic models (schemas)
====================================

In lesson 1 we described the request body field by field with Body().
That gets messy fast. A Pydantic model lets us describe the shape ONCE
and reuse it, and we get validation + docs for free.

Vocabulary you will keep hearing:
    request schema  -> what the client is allowed to send us
    response schema -> what we promise to send back
"""

from datetime import datetime
from enum import Enum
from random import randint
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def random_destination() -> int:
    """Generate a pseudo-random shipment id.

    NOTE: This does not guarantee uniqueness against existing ids in the
    in-memory store (data.py uses ids 1001-1020, which overlaps this
    range). Fine for demo purposes, but a real system should use a proper
    id sequence / UUID / database autoincrement instead.
    """
    return randint(1000, 2000)


# Inheriting from `str` as well as `Enum` means the value behaves like a
# normal string, so it serialises straight to JSON as "placed" etc.
class ShipmentStatus(str, Enum):
    """Lifecycle states a shipment can be in."""

    PLACED = "placed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# A "base" model holds the fields every other model shares. The other
# models inherit from it so we don't repeat content/weight everywhere.
class ShipmentBase(BaseModel):
    """Shared fields common to every shipment representation."""

    # json_schema_extra only affects the example shown on /docs.
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"content": "Electronics", "weight": 12.5}
        }
    )

    # Field() adds validation rules + documentation to a single field.
    # Break a rule and FastAPI answers 422 automatically, you write no code.
    content: str = Field(
        min_length=1,
        max_length=30,
        description="Description of the shipment contents. Cannot be empty.",
    )
    weight: float = Field(
        gt=0,          # gt = greater than
        le=100,        # le = less than or equal
        description="Weight of the shipment in kilograms (KG).",
    )


class Ships(ShipmentBase):
    """Request schema used when creating a new shipment."""

    # Literal restricts the value to this exact list of strings.
    # (An Enum like ShipmentStatus above is the other way to do this.)
    status: Literal[
        "placed", "in_transit", "delivered", "out_for_delivery"
    ] = "placed"
    destination: str = Field(min_length=1, max_length=100)
    estimated_delivery: datetime


class ShipmentRead(ShipmentBase):
    """Response schema for returning a shipment with its id."""

    id: int
    status: str


class ShipmentUpdate(ShipmentBase):
    """Request schema for updating a shipment.

    It has no extra fields of its own - it just reuses content + weight
    from ShipmentBase. It exists as a separate name so that later, when
    update rules differ from create rules, you only change this class.
    """


class ResponseModel(ShipmentBase):
    """Full shipment representation returned after creation."""

    # default_factory calls the function when a value is not supplied.
    id: int = Field(default_factory=random_destination)
    status: ShipmentStatus
