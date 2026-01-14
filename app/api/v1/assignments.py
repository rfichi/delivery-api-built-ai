from fastapi import APIRouter, HTTPException, Depends, Header
from app.schemas.assignments import AssignmentCreate, AssignmentRead, AssignmentStatus
from app.services import assignments as service
from app.core.security import get_current_user
from app.core.idempotency import execute_with_idempotency


router = APIRouter(prefix="/assignments", tags=["assignments"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=AssignmentRead)
async def create(payload: AssignmentCreate, idempotency_key: str | None = Header(None, alias="Idempotency-Key"), user=Depends(get_current_user)):
    async def handler():
        a = await service.create_assignment(payload)
        if not a:
            raise HTTPException(status_code=400, detail="invalid_order_or_courier")
        return a
    return await execute_with_idempotency(idempotency_key, "POST /v1/assignments", user["username"], payload.model_dump(), handler)


@router.get("/{assignment_id}", response_model=AssignmentRead)
async def read(assignment_id: str):
    a = await service.get_assignment(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    return a


@router.patch("/{assignment_id}/status", response_model=AssignmentRead)
async def set_status(assignment_id: str, status: AssignmentStatus):
    a = await service.set_status(assignment_id, status)
    if not a:
        raise HTTPException(status_code=404, detail="assignment_not_found")
    return a
