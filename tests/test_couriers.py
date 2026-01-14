from fastapi.testclient import TestClient
from app.main import app


def get_token(client: TestClient):
    res = client.post("/v1/auth/token", data={"username": "admin", "password": "test"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_create_and_get_courier():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        c = client.post("/v1/couriers", headers=headers, json={"name": "Alex", "vehicle_type": "bike"}).json()
        got = client.get(f"/v1/couriers/{c['id']}", headers=headers).json()
    assert got["name"] == "Alex"
    assert got["available"] is True


def test_update_availability_and_location():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        c = client.post("/v1/couriers", headers=headers, json={"name": "Sam", "vehicle_type": "car"}).json()
        updated = client.patch(f"/v1/couriers/{c['id']}/availability", headers=headers, json={"available": False}).json()
    assert updated["available"] is False
    ok = client.post(f"/v1/couriers/{c['id']}/location", headers=headers, json={"lat": 40.7, "lon": -74.0}).json()
    assert ok["updated"] is True


def test_update_location_invalid_courier():
    with TestClient(app) as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        r = client.post("/v1/couriers/missing/location", headers=headers, json={"lat": 0.0, "lon": 0.0})
    assert r.status_code == 404
