import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.case import Case
from app.models.beneficiary import Beneficiary
from app.models.assessment import Assessment
from app.models.eligibility_result import EligibilityResult
from app.models.action_plan import ActionStep
from app.models.shareable_link import ShareableLink
from app.schemas.shareable_link import ShareableLinkOut, CitizenRecordOut
from app.routers.eligibility import _to_out

router = APIRouter(tags=["shareable-links"])


@router.post("/cases/{case_id}/share", response_model=ShareableLinkOut, status_code=201)
def create_share_link(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.query(Case).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    link = ShareableLink(case_id=case_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return ShareableLinkOut(token=link.token, url_path=f"/citizen-record/{link.token}")


@router.get("/citizen-record/{token}", response_model=CitizenRecordOut)
def get_citizen_record(token: str, db: Session = Depends(get_db)):
    """Public, read-only — no auth required, matches the Citizen Record
    screen which a worker shows directly to the citizen."""
    link = db.query(ShareableLink).filter(ShareableLink.token == token).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found or expired")

    case = db.query(Case).get(link.case_id)
    beneficiary = db.query(Beneficiary).get(case.beneficiary_id)
    assessment = db.query(Assessment).filter(Assessment.case_id == case.id).order_by(
        Assessment.created_at.desc()
    ).first()
    results = db.query(EligibilityResult).filter(
        EligibilityResult.assessment_id == assessment.id
    ).all() if assessment else []
    schemes_out = _to_out(db, results)

    next_step = db.query(ActionStep).filter(
        ActionStep.case_id == case.id, ActionStep.status != "completed"
    ).order_by(ActionStep.order_index).first()

    return CitizenRecordOut(
        beneficiary=beneficiary,
        eligible_count=len([r for r in schemes_out if r.status == "eligible"]),
        schemes=schemes_out,
        next_step=next_step,
    )
