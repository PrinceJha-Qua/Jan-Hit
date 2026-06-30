import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON

from app.database import Base, GUID


class EligibilityResult(Base):
    __tablename__ = "eligibility_results"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(GUID(), ForeignKey("assessments.id"), nullable=False)
    scheme_id = Column(GUID(), ForeignKey("schemes.id"), nullable=False)
    status = Column(String, nullable=False)  # eligible|pending|needs-documents
    why_eligible = Column(String, nullable=False)
    missing_documents = Column(JSON, default=list)
    next_step = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
