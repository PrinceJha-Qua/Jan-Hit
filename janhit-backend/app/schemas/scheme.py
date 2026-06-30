import uuid
from typing import Optional, List, Literal
from pydantic import BaseModel


class SchemeOut(BaseModel):
    id: uuid.UUID
    name: str
    department: str
    benefit_amount: str

    class Config:
        from_attributes = True


class SchemeCreate(BaseModel):
    name: str
    department: str
    benefit_amount: str
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_annual_income: Optional[int] = None
    requires_widow: Optional[bool] = None
    requires_farmer: Optional[bool] = None
    requires_disability: Optional[bool] = None
    allowed_genders: Optional[List[str]] = None
    allowed_districts: Optional[List[str]] = None
    required_documents: List[str] = []
    next_step_template: str
    why_eligible_template: str


EligibilityStatus = Literal["eligible", "pending", "needs-documents"]


class EligibilityResultOut(BaseModel):
    id: uuid.UUID
    scheme_id: uuid.UUID
    scheme_name: str
    department: str
    benefit_amount: str
    status: EligibilityStatus
    why_eligible: str
    missing_documents: List[str]
    next_step: str

    class Config:
        from_attributes = True
