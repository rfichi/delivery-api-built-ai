import pytest
from fastapi.testclient import TestClient
from app.main import app


def get_token(client: TestClient):
    res = client.post("/v1/auth/token", data={"username": "admin", "password": "test"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_order_version_increments_on_status_change():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        body = {"customer_id": "v1", "pickup_address": "A", "dropoff_address": "B"}
        r = client.post("/v1/orders", headers=headers, json=body)
        assert r.status_code == 200
        order = r.json()
        assert order["version"] == 0
        r2 = client.patch(f"/v1/orders/{order['id']}/status", headers=headers, params={"status": "delivered"})
        assert r2.status_code == 200
        order2 = r2.json()
    assert order2["version"] == 1


def test_assignment_version_increments_on_set_status():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        o = client.post("/v1/orders", headers=headers, json={"customer_id": "v2", "pickup_address": "A", "dropoff_address": "B"}).json()
        c = client.post("/v1/couriers", headers=headers, json={"name": "Tester", "vehicle_type": "bike"}).json()
        a = client.post("/v1/assignments", headers=headers, json={"order_id": o["id"], "courier_id": c["id"]}).json()
        assert a["version"] == 0
        a2 = client.patch(f"/v1/assignments/{a['id']}/status", headers=headers, params={"status": "completed"}).json()
    assert a2["version"] == 1
