"""Seed the 4 demo schemes from lib/demo-data.ts as real rule rows.
Run with: python -m app.seed
"""
from app.database import SessionLocal
from app.models.scheme import Scheme

SCHEMES = [
    dict(
        name="Indira Gandhi National Old Age Pension (IGNOAPS)",
        department="Ministry of Rural Development",
        benefit_amount="₹500/month (Centre) + ₹600/month (State)",
        min_age=60,
        max_annual_income=100000,
        requires_widow=True,
        required_documents=["Income Certificate", "Death Certificate of Spouse"],
        next_step_template="Obtain Income Certificate from Tehsil office",
        why_eligible_template="Age 60+, widow, income below ₹1 lakh/year",
    ),
    dict(
        name="National Family Benefit Scheme (NFBS)",
        department="Ministry of Women & Child Development",
        benefit_amount="₹20,000 one-time",
        max_annual_income=100000,
        requires_widow=True,
        required_documents=["BPL Card", "Death Certificate"],
        next_step_template="Verify BPL status with Gram Panchayat",
        why_eligible_template="BPL family, primary breadwinner deceased",
    ),
    dict(
        name="Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
        department="Ministry of Health & Family Welfare",
        benefit_amount="₹5 lakh health cover per family/year",
        required_documents=["Ration Card", "Aadhaar Card"],
        next_step_template="Verify SECC listing at CSC centre",
        why_eligible_template="Rural household, SECC listed, no insurance",
    ),
    dict(
        name="Widow Pension Scheme (State)",
        department="Social Welfare Department, Maharashtra",
        benefit_amount="₹600/month",
        min_age=18,
        requires_widow=True,
        allowed_districts=None,  # state-wide; tighten later per-state if needed
        required_documents=["Domicile Certificate", "Bank Passbook"],
        next_step_template="Apply online via MahaDBT portal",
        why_eligible_template="Resident, widow, age 18+",
    ),
]


def seed():
    db = SessionLocal()
    try:
        if db.query(Scheme).count() > 0:
            print("Schemes already seeded, skipping.")
            return
        for data in SCHEMES:
            db.add(Scheme(**data))
        db.commit()
        print(f"Seeded {len(SCHEMES)} schemes.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
