from sqlalchemy import String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.schemas.assignments import AssignmentStatus


class Assignment(Base):
    __tablename__ = "assignments"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.id"))
    courier_id: Mapped[str] = mapped_column(String, ForeignKey("couriers.id"))
    status: Mapped[AssignmentStatus] = mapped_column(SAEnum(AssignmentStatus, native_enum=False, create_constraint=False))
    version: Mapped[int] = mapped_column(default=0)
