from fastapi import APIRouter, HTTPException, Depends, Header
from app.schemas.couriers import CourierCreate, CourierRead, CourierAvailabilityUpdate, LocationUpdate
from app.services import couriers as service
from app.core.security import get_current_user
from app.core.idempotency import execute_with_idempotency


router = APIRouter(prefix="/couriers", tags=["couriers"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=CourierRead)
async def create(payload: CourierCreate, idempotency_key: str | None = Header(None, alias="Idempotency-Key"), user=Depends(get_current_user)):
    async def handler():
        return await service.create_courier(payload)
    return await execute_with_idempotency(idempotency_key, "POST /v1/couriers", user["username"], payload.model_dump(), handler)


@router.get("/{courier_id}", response_model=CourierRead)
async def read(courier_id: str):
    courier = await service.get_courier(courier_id)
    if not courier:
        raise HTTPException(status_code=404, detail="courier_not_found")
    return courier


@router.patch("/{courier_id}/availability", response_model=CourierRead)
async def set_availability(courier_id: str, payload: CourierAvailabilityUpdate):
    courier = await service.update_availability(courier_id, payload)
    if not courier:
        raise HTTPException(status_code=404, detail="courier_not_found")
    return courier


@router.post("/{courier_id}/location")
async def set_location(courier_id: str, payload: LocationUpdate):
    ok = await service.update_location(courier_id, payload)
    if not ok:
        raise HTTPException(status_code=404, detail="courier_not_found")
    return {"updated": True}
