import uuid
from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel

StepStatus = Literal["completed", "in-progress", "pending", "blocked"]


class ActionStepOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: StepStatus
    owner: str
    due_date: Optional[date]

    class Config:
        from_attributes = True


class ActionStepUpdate(BaseModel):
    status: StepStatus
