import uuid
from sqlalchemy import Column, String, Integer, Boolean, JSON

from app.database import Base, GUID


class Scheme(Base):
    """A welfare scheme and the deterministic rules that decide eligibility.

    No LLM, no scoring model. Every field here is a plain rule checked with
    simple comparisons in eligibility_engine.py. Null on a rule field means
    'no constraint' (the rule is skipped). List fields use JSON so the same
    model works on SQLite (dev) and Postgres (prod) without two code paths.
    """

    __tablename__ = "schemes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    benefit_amount = Column(String, nullable=False)

    # --- rule fields (deterministic, all optional / nullable = unconstrained) ---
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    max_annual_income = Column(Integer, nullable=True)
    requires_widow = Column(Boolean, nullable=True)
    requires_farmer = Column(Boolean, nullable=True)
    requires_disability = Column(Boolean, nullable=True)
    allowed_genders = Column(JSON, nullable=True)
    allowed_districts = Column(JSON, nullable=True)  # null = all districts

    required_documents = Column(JSON, nullable=False, default=list)
    next_step_template = Column(String, nullable=False)
    why_eligible_template = Column(String, nullable=False)
