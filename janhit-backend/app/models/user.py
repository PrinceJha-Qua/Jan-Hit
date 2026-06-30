import uuid
from sqlalchemy import Column, String

from app.database import Base, GUID


class User(Base):
    """Frontline worker account. Auth (JWT) is deferred to v2 — this table
    exists now so cases can reference an owner without a future migration."""

    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    role = Column(String, default="field_worker")
    district = Column(String, nullable=True)
