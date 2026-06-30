import uuid
from pydantic import BaseModel

from app.schemas.beneficiary import BeneficiaryOut
from app.schemas.scheme import EligibilityResultOut
from app.schemas.action_plan import ActionStepOut
from typing import List


class ShareableLinkOut(BaseModel):
    token: str
    url_path: str


class CitizenRecordOut(BaseModel):
    beneficiary: BeneficiaryOut
    eligible_count: int
    schemes: List[EligibilityResultOut]
    next_step: ActionStepOut | None
