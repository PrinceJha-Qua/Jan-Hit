import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime

from app.database import Base, GUID


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # created|updated|deleted
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
