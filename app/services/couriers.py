import uuid
from typing import Optional
from sqlalchemy import select
from app.schemas.couriers import (
    CourierCreate,
    CourierRead,
    CourierStatus,
    CourierAvailabilityUpdate,
    LocationUpdate,
)
from app.models.courier import Courier
from app.db.session import SessionLocal


def to_read(c: Courier) -> CourierRead:
    return CourierRead(
        id=c.id,
        name=c.name,
        vehicle_type=c.vehicle_type,
        status=c.status,
        available=c.available,
    )


async def create_courier(payload: CourierCreate) -> CourierRead:
    async with SessionLocal() as session:
        cid = str(uuid.uuid4())
        obj = Courier(
            id=cid,
            name=payload.name,
            vehicle_type=payload.vehicle_type,
            status=CourierStatus.active,
            available=True,
        )
        session.add(obj)
        await session.commit()
        return to_read(obj)


async def get_courier(courier_id: str) -> Optional[CourierRead]:
    async with SessionLocal() as session:
        res = await session.execute(select(Courier).where(Courier.id == courier_id))
        obj = res.scalar_one_or_none()
        return to_read(obj) if obj else None


async def update_availability(courier_id: str, payload: CourierAvailabilityUpdate) -> Optional[CourierRead]:
    async with SessionLocal() as session:
        res = await session.execute(select(Courier).where(Courier.id == courier_id))
        obj = res.scalar_one_or_none()
        if not obj:
            return None
        obj.available = payload.available
        await session.commit()
        await session.refresh(obj)
        return to_read(obj)


_locations: dict[str, LocationUpdate] = {}


async def update_location(courier_id: str, payload: LocationUpdate) -> bool:
    async with SessionLocal() as session:
        res = await session.execute(select(Courier).where(Courier.id == courier_id))
        obj = res.scalar_one_or_none()
        if not obj:
            return False
        _locations[courier_id] = payload
        return True
