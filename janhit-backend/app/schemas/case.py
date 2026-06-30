import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel

CaseStatus = Literal["pending", "in-progress", "completed", "needs-follow-up"]


class CaseCreate(BaseModel):
    beneficiary_id: uuid.UUID


class CaseUpdate(BaseModel):
    status: CaseStatus


class CaseOut(BaseModel):
    id: uuid.UUID
    beneficiary_id: uuid.UUID
    status: CaseStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
