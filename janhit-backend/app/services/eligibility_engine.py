"""
Deterministic eligibility engine.

Every decision here is a plain comparison against fields on Scheme.
There is no model, no score, no probability — a beneficiary either
satisfies a rule or does not. This file is intentionally boring:
boring is auditable, and government eligibility must be auditable.
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.beneficiary import Beneficiary
from app.models.scheme import Scheme
from app.models.eligibility_result import EligibilityResult


def _rule_failures(beneficiary: Beneficiary, scheme: Scheme) -> List[str]:
    """Return the list of rules a beneficiary fails for a scheme.
    Empty list = fully eligible. Used to decide status + why_eligible text."""
    failures = []

    if scheme.min_age is not None and beneficiary.age < scheme.min_age:
        failures.append(f"age below {scheme.min_age}")
    if scheme.max_age is not None and beneficiary.age > scheme.max_age:
        failures.append(f"age above {scheme.max_age}")
    if scheme.max_annual_income is not None and beneficiary.annual_income > scheme.max_annual_income:
        failures.append(f"income above ₹{scheme.max_annual_income}")
    if scheme.requires_widow and not beneficiary.is_widow:
        failures.append("not recorded as widow")
    if scheme.requires_farmer and not beneficiary.is_farmer:
        failures.append("not recorded as farmer")
    if scheme.requires_disability and not beneficiary.has_disability:
        failures.append("no recorded disability")
    if scheme.allowed_genders and beneficiary.gender not in scheme.allowed_genders:
        failures.append("gender not covered")
    if scheme.allowed_districts and beneficiary.district not in scheme.allowed_districts:
        failures.append("district not covered")

    return failures


def evaluate_scheme(beneficiary: Beneficiary, scheme: Scheme) -> dict | None:
    """Evaluate a single scheme against a beneficiary.
    Returns None if hard-disqualified by district/gender (scheme doesn't apply
    at all), otherwise a dict describing status/why/missing docs/next step."""
    failures = _rule_failures(beneficiary, scheme)

    # Hard mismatches (district/gender) mean the scheme is not relevant —
    # we don't show it at all rather than confuse the worker.
    hard_blockers = [f for f in failures if "district" in f or "gender" in f]
    if hard_blockers:
        return None

    soft_failures = [f for f in failures if f not in hard_blockers]

    if soft_failures:
        # Fails an income/age/category rule -> not eligible right now.
        return None

    # Passed every rule. Status depends only on whether documents are missing.
    missing_docs = list(scheme.required_documents or [])
    status = "needs-documents" if missing_docs else "eligible"

    return {
        "status": status,
        "why_eligible": scheme.why_eligible_template,
        "missing_documents": missing_docs,
        "next_step": scheme.next_step_template,
    }


def run_eligibility(db: Session, beneficiary: Beneficiary, assessment_id) -> List[EligibilityResult]:
    """Run every active scheme against one beneficiary and persist results.
    Pure rule evaluation — same input always produces the same output."""
    schemes = db.query(Scheme).all()
    results: List[EligibilityResult] = []

    for scheme in schemes:
        outcome = evaluate_scheme(beneficiary, scheme)
        if outcome is None:
            continue
        result = EligibilityResult(
            assessment_id=assessment_id,
            scheme_id=scheme.id,
            status=outcome["status"],
            why_eligible=outcome["why_eligible"],
            missing_documents=outcome["missing_documents"],
            next_step=outcome["next_step"],
        )
        db.add(result)
        results.append(result)

    db.commit()
    for r in results:
        db.refresh(r)
    return results
