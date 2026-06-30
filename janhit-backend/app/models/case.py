import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime

from app.database import Base, GUID


class Case(Base):
    __tablename__ = "cases"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    beneficiary_id = Column(GUID(), ForeignKey("beneficiaries.id"), nullable=False)
    status = Column(String, default="pending")  # pending|in-progress|completed|needs-follow-up
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
