from fastapi.testclient import TestClient
from app.main import app


def get_token(client: TestClient):
    res = client.post("/v1/auth/token", data={"username": "admin", "password": "test"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_create_assignment_and_complete():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        o = client.post("/v1/orders", headers=headers, json={"customer_id": "c1", "pickup_address": "A", "dropoff_address": "B"}).json()
        c = client.post("/v1/couriers", headers=headers, json={"name": "Alex", "vehicle_type": "bike"}).json()
        a = client.post("/v1/assignments", headers=headers, json={"order_id": o["id"], "courier_id": c["id"]}).json()
        final_order = client.get(f"/v1/orders/{o['id']}", headers=headers).json()
        assert a is not None
        a2 = client.patch(f"/v1/assignments/{a['id']}/status", headers=headers, params={"status": "completed"}).json()
        final_order = client.get(f"/v1/orders/{o['id']}", headers=headers).json()
    assert final_order["status"] == "delivered"


def test_assignment_invalid_entities():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        r = client.post("/v1/assignments", headers=headers, json={"order_id": "missing", "courier_id": "missing"})
    assert r.status_code == 400
