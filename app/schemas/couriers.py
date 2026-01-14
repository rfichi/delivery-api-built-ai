from enum import Enum
from pydantic import BaseModel


class CourierStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class CourierCreate(BaseModel):
    name: str
    vehicle_type: str


class CourierRead(BaseModel):
    id: str
    name: str
    vehicle_type: str
    status: CourierStatus
    available: bool


class CourierAvailabilityUpdate(BaseModel):
    available: bool


class LocationUpdate(BaseModel):
    lat: float
    lon: float
