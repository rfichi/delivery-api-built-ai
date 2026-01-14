from enum import Enum
from pydantic import BaseModel
from typing import Optional


class OrderStatus(str, Enum):
    created = "created"
    assigned = "assigned"
    picked_up = "picked_up"
    delivered = "delivered"
    canceled = "canceled"


class OrderCreate(BaseModel):
    customer_id: str
    pickup_address: str
    dropoff_address: str
    price: Optional[float] = None


class OrderRead(BaseModel):
    id: str
    customer_id: str
    pickup_address: str
    dropoff_address: str
    price: Optional[float] = None
    status: OrderStatus
    version: int
