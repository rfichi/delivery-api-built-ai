from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.schemas.couriers import CourierStatus


class Courier(Base):
    __tablename__ = "couriers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    vehicle_type: Mapped[str] = mapped_column(String)
    status: Mapped[CourierStatus] = mapped_column(SAEnum(CourierStatus, native_enum=False, create_constraint=False))
    available: Mapped[bool] = mapped_column(Boolean, default=True)
