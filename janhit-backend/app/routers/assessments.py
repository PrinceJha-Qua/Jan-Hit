from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.models.case import Case
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentOut

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentOut, status_code=201)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    """Matches the frontend's 'Find Schemes' button on step 4: one call
    creates the beneficiary, opens a case, and records the assessment."""
    beneficiary = Beneficiary(**payload.beneficiary.model_dump())
    db.add(beneficiary)
    db.flush()  # get beneficiary.id without committing yet

    case = Case(beneficiary_id=beneficiary.id, status="pending")
    db.add(case)
    db.flush()

    assessment = Assessment(case_id=case.id, beneficiary_id=beneficiary.id)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
