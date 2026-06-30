import uuid
from datetime import datetime
from pydantic import BaseModel

from app.schemas.beneficiary import BeneficiaryCreate


class AssessmentCreate(BaseModel):
    """Submitted from the 4-step frontend form. Creates the beneficiary
    + case + assessment in one call to match the single 'Find Schemes' action."""
    beneficiary: BeneficiaryCreate


class AssessmentOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    beneficiary_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
