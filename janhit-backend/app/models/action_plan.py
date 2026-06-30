import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Date

from app.database import Base, GUID


class ActionStep(Base):
    __tablename__ = "action_steps"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    case_id = Column(GUID(), ForeignKey("cases.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="pending")  # completed|in-progress|pending|blocked
    owner = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    order_index = Column(String, nullable=False, default="0")
    created_at = Column(DateTime, default=datetime.utcnow)
