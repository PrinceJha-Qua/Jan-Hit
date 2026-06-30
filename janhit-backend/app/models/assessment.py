import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime

from app.database import Base, GUID


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    case_id = Column(GUID(), ForeignKey("cases.id"), nullable=False)
    beneficiary_id = Column(GUID(), ForeignKey("beneficiaries.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
