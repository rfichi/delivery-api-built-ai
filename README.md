# Delivery API (FastAPI)

## Summary
- FastAPI-based Delivery system API supporting Orders, Couriers, and Assignments.
- JWT auth, Prometheus metrics, SQLite persistence with SQLAlchemy.
- Idempotency via Idempotency-Key header; version columns for optimistic concurrency readiness.

## Stack
- FastAPI, Starlette, Uvicorn
- Pydantic v2
- SQLAlchemy 2.0 (async) + SQLite (aiosqlite)
- JWT (PyJWT)
- Prometheus metrics (prometheus-fastapi-instrumentator)
- Testing: Pytest, TestClient/httpx

## Description
- Orders: create, read, list, status updates, cancel.
- Couriers: create, read, availability update, location update.
- Assignments: create, read, set status; completing an assignment marks the order delivered.
- Auth: OAuth2 password with JWT; roles demo users: admin, courier, customer (password: test).
- Idempotency: POST endpoints accept Idempotency-Key header to deduplicate requests and return the same response for repeated calls; conflicts return 409.
- Version columns: orders.version, assignments.version increment on updates; prepared for optimistic concurrency.
- Metrics: exposed at `/metrics` for scraping.

## Quick Start
1. Install deps:
   - Windows/PowerShell:
     - `pip install -r requirements.txt`
   - Linux/macOS:
     - `python -m pip install -r requirements.txt`
2. Run dev server:
   - `python -m uvicorn app.main:app --reload --port 8000`
3. Health:
   - `http://127.0.0.1:8000/v1/health`
4. Metrics:
   - `http://127.0.0.1:8000/metrics`

## Auth
- Obtain token (form-encoded):
  - Windows/PowerShell:
    - `$token = (Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/auth/token -Body "username=admin&password=test" -ContentType "application/x-www-form-urlencoded").access_token`
  - Linux/macOS (curl):
    - `TOKEN=$(curl -s -X POST http://127.0.0.1:8000/v1/auth/token -d "username=admin&password=test" | jq -r .access_token)`
    - If jq not installed, use: `TOKEN=$(curl -s -X POST http://127.0.0.1:8000/v1/auth/token -d "username=admin&password=test" | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")`

## Endpoints
- Base URL: `http://127.0.0.1:8000/v1`
- Use `Authorization: Bearer <token>` for all endpoints below.
- Idempotent POST: add header `Idempotency-Key: <unique-string>` when desired.

### Health
- GET `/health`
  - Windows: `Invoke-RestMethod -Uri http://127.0.0.1:8000/v1/health`
  - Linux: `curl http://127.0.0.1:8000/v1/health`

### Orders
- POST `/orders`
  - Windows: `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/orders -Headers @{Authorization="Bearer $token"} -ContentType 'application/json' -Body '{"customer_id":"c1","pickup_address":"A","dropoff_address":"B","price":10.0}'`
  - Linux: `curl -X POST http://127.0.0.1:8000/v1/orders -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"customer_id":"c1","pickup_address":"A","dropoff_address":"B","price":10.0}'`
  - Idempotency: add `-H "Idempotency-Key: key-123"` (Linux) or `-Headers @{Authorization="Bearer $token";"Idempotency-Key"="key-123"}` (Windows).
- GET `/orders/{id}`
  - Windows: `Invoke-RestMethod -Uri http://127.0.0.1:8000/v1/orders/<id> -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl http://127.0.0.1:8000/v1/orders/<id> -H "Authorization: Bearer $TOKEN"`
- GET `/orders?status=delivered`
  - Windows: `Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/orders?status=delivered" -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl "http://127.0.0.1:8000/v1/orders?status=delivered" -H "Authorization: Bearer $TOKEN"`
- PATCH `/orders/{id}/status?status=<value>`
  - Windows: `Invoke-RestMethod -Method Patch -Uri "http://127.0.0.1:8000/v1/orders/<id>/status?status=delivered" -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl -X PATCH "http://127.0.0.1:8000/v1/orders/<id>/status?status=delivered" -H "Authorization: Bearer $TOKEN"`
- DELETE `/orders/{id}`
  - Windows: `Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/v1/orders/<id> -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl -X DELETE http://127.0.0.1:8000/v1/orders/<id> -H "Authorization: Bearer $TOKEN"`

### Couriers
- POST `/couriers`
  - Windows: `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/couriers -Headers @{Authorization="Bearer $token"} -ContentType 'application/json' -Body '{"name":"Dana","vehicle_type":"bike"}'`
  - Linux: `curl -X POST http://127.0.0.1:8000/v1/couriers -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"name":"Dana","vehicle_type":"bike"}'`
- GET `/couriers/{id}`
  - Windows: `Invoke-RestMethod -Uri http://127.0.0.1:8000/v1/couriers/<id> -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl http://127.0.0.1:8000/v1/couriers/<id> -H "Authorization: Bearer $TOKEN"`
- PATCH `/couriers/{id}/availability`
  - Windows: `Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/v1/couriers/<id>/availability -Headers @{Authorization="Bearer $token"} -ContentType 'application/json' -Body '{"available":false}'`
  - Linux: `curl -X PATCH http://127.0.0.1:8000/v1/couriers/<id>/availability -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"available":false}'`
- POST `/couriers/{id}/location`
  - Windows: `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/couriers/<id>/location -Headers @{Authorization="Bearer $token"} -ContentType 'application/json' -Body '{"lat":40.7,"lon":-74.0}'`
  - Linux: `curl -X POST http://127.0.0.1:8000/v1/couriers/<id>/location -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"lat":40.7,"lon":-74.0}'`

### Assignments
- POST `/assignments`
  - Windows (PowerShell convert JSON body): 
    - `$body = @{ order_id = "<orderId>"; courier_id = "<courierId>" } | ConvertTo-Json`
    - `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/assignments -Headers @{Authorization="Bearer $token"} -ContentType 'application/json' -Body $body`
  - Linux: `curl -X POST http://127.0.0.1:8000/v1/assignments -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"order_id":"<orderId>","courier_id":"<courierId>"}'`
- GET `/assignments/{id}`
  - Windows: `Invoke-RestMethod -Uri http://127.0.0.1:8000/v1/assignments/<id> -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl http://127.0.0.1:8000/v1/assignments/<id> -H "Authorization: Bearer $TOKEN"`
- PATCH `/assignments/{id}/status?status=completed|accepted|declined`
  - Windows: `Invoke-RestMethod -Method Patch -Uri "http://127.0.0.1:8000/v1/assignments/<id>/status?status=completed" -Headers @{Authorization="Bearer $token"}`
  - Linux: `curl -X PATCH "http://127.0.0.1:8000/v1/assignments/<id>/status?status=completed" -H "Authorization: Bearer $TOKEN"`

## Notes
- Startup recreates tables on each run for simplicity in development and testing.
- Idempotency tables store request hash and response to ensure consistent replies to duplicate requests.
