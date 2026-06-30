import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryOut

router = APIRouter(prefix="/beneficiaries", tags=["beneficiaries"])


@router.post("", response_model=BeneficiaryOut, status_code=201)
def create_beneficiary(payload: BeneficiaryCreate, db: Session = Depends(get_db)):
    b = Beneficiary(**payload.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.get("/{beneficiary_id}", response_model=BeneficiaryOut)
def get_beneficiary(beneficiary_id: uuid.UUID, db: Session = Depends(get_db)):
    b = db.query(Beneficiary).get(beneficiary_id)
    if not b:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return b
