from fastapi.testclient import TestClient
from app.main import app


def get_token(client: TestClient):
    res = client.post("/v1/auth/token", data={"username": "admin", "password": "test"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_create_and_get_order():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        o = client.post("/v1/orders", headers=headers, json={"customer_id": "c1", "pickup_address": "A", "dropoff_address": "B", "price": 10.0}).json()
        got = client.get(f"/v1/orders/{o['id']}", headers=headers).json()
    assert got["customer_id"] == "c1"
    assert got["status"] == "created"


def test_list_orders_by_status():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        o1 = client.post("/v1/orders", headers=headers, json={"customer_id": "c1", "pickup_address": "A", "dropoff_address": "B"}).json()
        o2 = client.post("/v1/orders", headers=headers, json={"customer_id": "c2", "pickup_address": "C", "dropoff_address": "D"}).json()
        client.patch(f"/v1/orders/{o1['id']}/status", headers=headers, params={"status": "delivered"})
        delivered = client.get("/v1/orders", headers=headers, params={"status": "delivered"}).json()
    assert any(d["id"] == o1["id"] for d in delivered)


def test_cancel_order():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        o = client.post("/v1/orders", headers=headers, json={"customer_id": "c1", "pickup_address": "A", "dropoff_address": "B"}).json()
        canceled = client.delete(f"/v1/orders/{o['id']}", headers=headers).json()
    assert canceled["status"] == "canceled"
