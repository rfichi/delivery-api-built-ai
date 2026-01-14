import uuid
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orders import OrderCreate, OrderRead, OrderStatus
from app.models.order import Order
from app.db.session import SessionLocal


def to_read(o: Order) -> OrderRead:
    return OrderRead(
        id=o.id,
        customer_id=o.customer_id,
        pickup_address=o.pickup_address,
        dropoff_address=o.dropoff_address,
        price=o.price,
        status=o.status,
        version=o.version,
    )


async def create_order(payload: OrderCreate) -> OrderRead:
    async with SessionLocal() as session:
        oid = str(uuid.uuid4())
        obj = Order(
            id=oid,
            customer_id=payload.customer_id,
            pickup_address=payload.pickup_address,
            dropoff_address=payload.dropoff_address,
            price=payload.price,
            status=OrderStatus.created,
        )
        session.add(obj)
        await session.commit()
        return to_read(obj)


async def get_order(order_id: str) -> Optional[OrderRead]:
    async with SessionLocal() as session:
        res = await session.execute(select(Order).where(Order.id == order_id))
        obj = res.scalar_one_or_none()
        return to_read(obj) if obj else None


async def list_orders(status: Optional[OrderStatus] = None) -> List[OrderRead]:
    async with SessionLocal() as session:
        stmt = select(Order)
        if status is not None:
            stmt = stmt.where(Order.status == status)
        res = await session.execute(stmt)
        return [to_read(o) for o in res.scalars().all()]


async def update_status(order_id: str, status: OrderStatus) -> Optional[OrderRead]:
    async with SessionLocal() as session:
        res = await session.execute(select(Order).where(Order.id == order_id))
        obj = res.scalar_one_or_none()
        if not obj:
            return None
        obj.status = status
        obj.version = (obj.version or 0) + 1
        await session.commit()
        await session.refresh(obj)
        return to_read(obj)


async def cancel_order(order_id: str) -> Optional[OrderRead]:
    return await update_status(order_id, OrderStatus.canceled)
