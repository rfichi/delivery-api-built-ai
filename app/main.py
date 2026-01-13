from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.v1 import health, orders, couriers, assignments, auth
from app.services.orders import create_order
from app.services.couriers import create_courier
from app.services.assignments import create_assignment
from app.schemas.orders import OrderCreate
from app.schemas.couriers import CourierCreate
from app.schemas.assignments import AssignmentCreate
from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.session import engine
from app.db.base import Base


def create_app() -> FastAPI:
    app = FastAPI(title="Delivery API", version="1.0.0")
    app.include_router(auth.router, prefix="/v1")
    app.include_router(health.router, prefix="/v1")
    app.include_router(orders.router, prefix="/v1")
    app.include_router(couriers.router, prefix="/v1")
    app.include_router(assignments.router, prefix="/v1")
    Instrumentator().instrument(app).expose(app)

    @app.on_event("startup")
    async def seed_data():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        o1 = await create_order(OrderCreate(customer_id="c1", pickup_address="A", dropoff_address="B", price=10.0))
        o2 = await create_order(OrderCreate(customer_id="c2", pickup_address="C", dropoff_address="D", price=12.5))
        o3 = await create_order(OrderCreate(customer_id="c3", pickup_address="E", dropoff_address="F", price=9.99))
        c1 = await create_courier(CourierCreate(name="Alex", vehicle_type="bike"))
        c2 = await create_courier(CourierCreate(name="Sam", vehicle_type="car"))
        await create_assignment(AssignmentCreate(order_id=o1.id, courier_id=c1.id))
        await create_assignment(AssignmentCreate(order_id=o2.id, courier_id=c2.id))
    return app


app = create_app()
