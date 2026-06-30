import uuid
import secrets
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime

from app.database import Base, GUID


def generate_token() -> str:
    return secrets.token_urlsafe(16)


class ShareableLink(Base):
    __tablename__ = "shareable_links"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    case_id = Column(GUID(), ForeignKey("cases.id"), nullable=False)
    token = Column(String, unique=True, default=generate_token, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
