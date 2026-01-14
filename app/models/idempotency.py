from sqlalchemy import String, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String)
    endpoint: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(String)
    request_hash: Mapped[str] = mapped_column(String)
    response_json: Mapped[str] = mapped_column(Text)
    status_code: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("key", "endpoint", "actor_id", name="uq_idem_key_endpoint_actor"),)
