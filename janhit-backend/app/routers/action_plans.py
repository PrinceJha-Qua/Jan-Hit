import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.case import Case
from app.models.assessment import Assessment
from app.models.eligibility_result import EligibilityResult
from app.models.action_plan import ActionStep
from app.schemas.action_plan import ActionStepOut, ActionStepUpdate
from app.services.action_plan_generator import generate_action_plan

router = APIRouter(tags=["action-plans"])


@router.post("/cases/{case_id}/action-plan", response_model=list[ActionStepOut], status_code=201)
def create_action_plan(case_id: uuid.UUID, db: Session = Depends(get_db)):
    """Backs the 'Generate Action Plan' button. Pulls the latest eligibility
    results for this case's assessment and builds the timeline."""
    case = db.query(Case).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    assessment = db.query(Assessment).filter(Assessment.case_id == case_id).order_by(
        Assessment.created_at.desc()
    ).first()
    if not assessment:
        raise HTTPException(status_code=400, detail="No assessment found for this case")

    results = db.query(EligibilityResult).filter(
        EligibilityResult.assessment_id == assessment.id
    ).all()
    if not results:
        raise HTTPException(status_code=400, detail="Run eligibility before generating an action plan")

    steps = generate_action_plan(db, case_id, results)
    return steps


@router.get("/cases/{case_id}/action-plan", response_model=list[ActionStepOut])
def get_action_plan(case_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.query(ActionStep).filter(ActionStep.case_id == case_id).order_by(
        ActionStep.order_index
    ).all()


@router.patch("/action-steps/{step_id}", response_model=ActionStepOut)
def update_action_step(step_id: uuid.UUID, payload: ActionStepUpdate, db: Session = Depends(get_db)):
    step = db.query(ActionStep).get(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    step.status = payload.status
    db.commit()
    db.refresh(step)
    return step
