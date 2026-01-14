import pytest
from fastapi.testclient import TestClient
from app.main import app


def get_token(client: TestClient):
    res = client.post("/v1/auth/token", data={"username": "admin", "password": "test"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_orders_idempotency_same_body():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "key-123"}
        body = {"customer_id": "idem1", "pickup_address": "A", "dropoff_address": "B", "price": 10.0}
        r1 = client.post("/v1/orders", headers=headers, json=body)
        r2 = client.post("/v1/orders", headers=headers, json=body)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_orders_idempotency_conflict():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": "key-456"}
        body1 = {"customer_id": "idem2", "pickup_address": "A", "dropoff_address": "B", "price": 10.0}
        body2 = {"customer_id": "idem2", "pickup_address": "A", "dropoff_address": "C", "price": 10.0}
        r1 = client.post("/v1/orders", headers=headers, json=body1)
        r2 = client.post("/v1/orders", headers=headers, json=body2)
    assert r1.status_code == 200
    assert r2.status_code == 409
