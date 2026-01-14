from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
from app.schemas.orders import OrderCreate, OrderRead, OrderStatus
from app.services import orders as service
from app.core.security import get_current_user
from app.core.idempotency import execute_with_idempotency


router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=OrderRead)
async def create(payload: OrderCreate, idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"), user=Depends(get_current_user)):
    async def handler():
        return await service.create_order(payload)
    return await execute_with_idempotency(idempotency_key, "POST /v1/orders", user["username"], payload.model_dump(), handler)


@router.get("/{order_id}", response_model=OrderRead)
async def read(order_id: str):
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order_not_found")
    return order


@router.get("", response_model=List[OrderRead])
async def list(status: Optional[OrderStatus] = None):
    return await service.list_orders(status)


@router.patch("/{order_id}/status", response_model=OrderRead)
async def patch_status(order_id: str, status: OrderStatus):
    order = await service.update_status(order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="order_not_found")
    return order


@router.delete("/{order_id}", response_model=OrderRead)
async def cancel(order_id: str):
    order = await service.cancel_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order_not_found")
    return order
