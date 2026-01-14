from enum import Enum
from pydantic import BaseModel


class AssignmentStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    completed = "completed"


class AssignmentCreate(BaseModel):
    order_id: str
    courier_id: str


class AssignmentRead(BaseModel):
    id: str
    order_id: str
    courier_id: str
    status: AssignmentStatus
    version: int
