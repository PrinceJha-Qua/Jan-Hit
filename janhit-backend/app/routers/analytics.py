from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.case import Case
from app.models.eligibility_result import EligibilityResult
from app.models.scheme import Scheme
from app.schemas.analytics import DistrictStatsOut, TopScheme, MonthlyTrend

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/district", response_model=DistrictStatsOut)
def district_stats(db: Session = Depends(get_db)):
    total_cases = db.query(Case).count()
    pending_cases = db.query(Case).filter(Case.status == "pending").count()

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    completed_this_month = db.query(Case).filter(
        Case.status == "completed", Case.updated_at >= month_start
    ).count()

    schemes_disbursed = db.query(EligibilityResult).filter(
        EligibilityResult.status == "eligible"
    ).count()

    top_rows = (
        db.query(Scheme.name, func.count(EligibilityResult.id).label("count"))
        .join(EligibilityResult, EligibilityResult.scheme_id == Scheme.id)
        .group_by(Scheme.name)
        .order_by(func.count(EligibilityResult.id).desc())
        .limit(5)
        .all()
    )
    top_schemes = [TopScheme(name=name, count=count) for name, count in top_rows]

    # Monthly trend: grouped in Python rather than with a DB-specific
    # date-formatting function, so this works identically on SQLite (dev)
    # and Postgres (prod) without dialect branching.
    all_cases = db.query(Case.created_at).order_by(Case.created_at).all()
    counts: dict[str, int] = {}
    for (created_at,) in all_cases:
        key = created_at.strftime("%b")
        counts[key] = counts.get(key, 0) + 1
    monthly_trend = [MonthlyTrend(month=m, cases=c) for m, c in counts.items()]

    return DistrictStatsOut(
        total_cases=total_cases,
        pending_cases=pending_cases,
        completed_this_month=completed_this_month,
        schemes_disbursed=schemes_disbursed,
        top_schemes=top_schemes,
        monthly_trend=monthly_trend,
    )
