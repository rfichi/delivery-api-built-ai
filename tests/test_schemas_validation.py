import pytest
from pydantic import ValidationError
from app.schemas.orders import OrderCreate
from app.schemas.couriers import LocationUpdate


def test_order_create_missing_fields():
    with pytest.raises(ValidationError):
        OrderCreate(customer_id="c1", pickup_address="A")  # missing dropoff_address


def test_location_update_type_validation():
    with pytest.raises(ValidationError):
        LocationUpdate(lat="not-a-float", lon=-74.0)
