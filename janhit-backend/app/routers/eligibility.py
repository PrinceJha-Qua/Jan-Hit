import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assessment import Assessment
from app.models.beneficiary import Beneficiary
from app.models.scheme import Scheme
from app.models.eligibility_result import EligibilityResult
from app.schemas.scheme import EligibilityResultOut
from app.services.eligibility_engine import run_eligibility

router = APIRouter(prefix="/assessments", tags=["eligibility"])


@router.post("/{assessment_id}/eligibility", response_model=list[EligibilityResultOut])
def compute_eligibility(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    """Backs the Eligibility Results screen. Deterministic — calling this
    twice for the same data always returns the same schemes."""
    assessment = db.query(Assessment).get(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    beneficiary = db.query(Beneficiary).get(assessment.beneficiary_id)
    results = run_eligibility(db, beneficiary, assessment_id)
    return _to_out(db, results)


@router.get("/{assessment_id}/eligibility", response_model=list[EligibilityResultOut])
def get_eligibility(assessment_id: uuid.UUID, db: Session = Depends(get_db)):
    results = db.query(EligibilityResult).filter(
        EligibilityResult.assessment_id == assessment_id
    ).all()
    return _to_out(db, results)


def _to_out(db: Session, results: list[EligibilityResult]) -> list[EligibilityResultOut]:
    out = []
    for r in results:
        scheme = db.query(Scheme).get(r.scheme_id)
        out.append(EligibilityResultOut(
            id=r.id,
            scheme_id=r.scheme_id,
            scheme_name=scheme.name,
            department=scheme.department,
            benefit_amount=scheme.benefit_amount,
            status=r.status,
            why_eligible=r.why_eligible,
            missing_documents=r.missing_documents or [],
            next_step=r.next_step,
        ))
    return out
