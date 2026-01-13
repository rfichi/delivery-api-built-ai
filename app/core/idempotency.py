import json
import time
import hashlib
from typing import Optional, Callable, Any, Dict
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.idempotency import IdempotencyRecord


def _hash_payload(payload: Dict[str, Any]) -> str:
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


async def execute_with_idempotency(
    idempotency_key: Optional[str],
    endpoint: str,
    actor_id: str,
    request_body: Dict[str, Any],
    handler: Callable[[], Any],
):
    if not idempotency_key:
        return await handler()
    req_hash = _hash_payload(request_body)
    async with SessionLocal() as session:
        existing = (
            await session.execute(
                select(IdempotencyRecord).where(
                    IdempotencyRecord.key == idempotency_key,
                    IdempotencyRecord.endpoint == endpoint,
                    IdempotencyRecord.actor_id == actor_id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            if existing.request_hash != req_hash:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="idempotency_conflict")
            return JSONResponse(content=json.loads(existing.response_json), status_code=existing.status_code)
        result = await handler()
        if hasattr(result, "model_dump"):
            payload = result.model_dump()
        else:
            payload = result if isinstance(result, dict) else json.loads(json.dumps(result, default=str))
        record = IdempotencyRecord(
            key=idempotency_key,
            endpoint=endpoint,
            actor_id=actor_id,
            request_hash=req_hash,
            response_json=json.dumps(payload, separators=(",", ":")),
            status_code=200,
            created_at=int(time.time()),
        )
        session.add(record)
        await session.commit()
        return result
