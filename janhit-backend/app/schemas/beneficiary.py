import uuid
from typing import Optional, Literal
from pydantic import BaseModel


class BeneficiaryCreate(BaseModel):
    name: str
    age: int
    district: str
    occupation: str
    annual_income: int
    is_widow: bool = False
    is_farmer: bool = False
    has_disability: bool = False
    caste: Optional[str] = None
    gender: Literal["female", "male", "other"]


class BeneficiaryOut(BeneficiaryCreate):
    id: uuid.UUID

    class Config:
        from_attributes = True
