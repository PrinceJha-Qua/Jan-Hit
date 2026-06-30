"""
Builds the Action Plan timeline from eligibility results.

One step per missing document, then one 'apply' step per eligible scheme,
then a standard follow-up step. Order matches what the frontend timeline
expects: documents first, then applications, then follow-up.
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.action_plan import ActionStep
from app.models.eligibility_result import EligibilityResult
from app.models.scheme import Scheme


def generate_action_plan(db: Session, case_id, results: list[EligibilityResult]) -> list[ActionStep]:
    steps: list[ActionStep] = []
    order = 0
    today = date.today()

    # Step 1..n: any missing document, deduplicated across schemes.
    seen_docs = set()
    for result in results:
        for doc in result.missing_documents:
            if doc in seen_docs:
                continue
            seen_docs.add(doc)
            steps.append(ActionStep(
                case_id=case_id,
                title=doc,
                description=f"Obtain {doc} required for scheme application",
                status="pending",
                owner="CSC Operator",
                due_date=today + timedelta(days=7 * (order + 1)),
                order_index=str(order),
            ))
            order += 1

    # One application step per eligible/needs-documents scheme.
    for result in results:
        scheme = db.query(Scheme).get(result.scheme_id)
        steps.append(ActionStep(
            case_id=case_id,
            title=f"Apply for {scheme.name}",
            description=f"Submit application for {scheme.name} via {scheme.department}",
            status="pending",
            owner="Gram Sevak",
            due_date=today + timedelta(days=7 * (order + 1)),
            order_index=str(order),
        ))
        order += 1

    # Final follow-up step, standard for every case.
    steps.append(ActionStep(
        case_id=case_id,
        title="Follow-up on sanction status",
        description="Check application/sanction status after 30 days",
        status="pending",
        owner="Gram Sevak",
        due_date=today + timedelta(days=30),
        order_index=str(order),
    ))

    db.add_all(steps)
    db.commit()
    for s in steps:
        db.refresh(s)
    return steps
