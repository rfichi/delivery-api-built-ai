from sqlalchemy import String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.schemas.orders import OrderStatus


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String)
    pickup_address: Mapped[str] = mapped_column(String)
    dropoff_address: Mapped[str] = mapped_column(String)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus, native_enum=False, create_constraint=False))
    version: Mapped[int] = mapped_column(default=0)
