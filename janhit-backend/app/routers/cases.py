import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.case import Case
from app.models.beneficiary import Beneficiary
from app.schemas.case import CaseOut, CaseUpdate

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseOut])
def list_cases(status: Optional[str] = None, district: Optional[str] = None, db: Session = Depends(get_db)):
    """Backs the Workspace screen tabs (Today's, Pending, Completed, Follow-up)."""
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    if district:
        query = query.join(Beneficiary).filter(Beneficiary.district == district)
    return query.order_by(Case.updated_at.desc()).all()


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    c = db.query(Case).get(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(case_id: uuid.UUID, payload: CaseUpdate, db: Session = Depends(get_db)):
    c = db.query(Case).get(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    c.status = payload.status
    db.commit()
    db.refresh(c)
    return c
