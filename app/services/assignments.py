import uuid
from typing import Optional
from sqlalchemy import select
from app.schemas.assignments import AssignmentCreate, AssignmentRead, AssignmentStatus
from app.schemas.orders import OrderStatus
from app.models.assignment import Assignment
from app.models.order import Order
from app.models.courier import Courier
from app.db.session import SessionLocal


def to_read(a: Assignment) -> AssignmentRead:
    return AssignmentRead(id=a.id, order_id=a.order_id, courier_id=a.courier_id, status=a.status, version=a.version)


async def create_assignment(payload: AssignmentCreate) -> Optional[AssignmentRead]:
    async with SessionLocal() as session:
        o = (await session.execute(select(Order).where(Order.id == payload.order_id))).scalar_one_or_none()
        c = (await session.execute(select(Courier).where(Courier.id == payload.courier_id))).scalar_one_or_none()
        if not o or not c:
            return None
        aid = str(uuid.uuid4())
        obj = Assignment(id=aid, order_id=payload.order_id, courier_id=payload.courier_id, status=AssignmentStatus.pending)
        session.add(obj)
        o.status = OrderStatus.assigned
        await session.commit()
        return to_read(obj)


async def get_assignment(assignment_id: str) -> Optional[AssignmentRead]:
    async with SessionLocal() as session:
        a = (await session.execute(select(Assignment).where(Assignment.id == assignment_id))).scalar_one_or_none()
        return to_read(a) if a else None


async def set_status(assignment_id: str, status: AssignmentStatus) -> Optional[AssignmentRead]:
    async with SessionLocal() as session:
        a = (await session.execute(select(Assignment).where(Assignment.id == assignment_id))).scalar_one_or_none()
        if not a:
            return None
        a.status = status
        a.version = (a.version or 0) + 1
        if status == AssignmentStatus.completed:
            o = (await session.execute(select(Order).where(Order.id == a.order_id))).scalar_one_or_none()
            if o:
                o.status = OrderStatus.delivered
                o.version = (o.version or 0) + 1
        await session.commit()
        await session.refresh(a)
        return to_read(a)
