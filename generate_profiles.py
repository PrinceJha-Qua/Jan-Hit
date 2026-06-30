"""
JanHit — 50 Realistic Maharashtra Citizen Profiles
----------------------------------------------------
Generates profiles across 8 demographic archetypes:
  Widows (10) · Farmers (10) · Students (8) · Senior Citizens (8)
  Agricultural Labor (6) · Disabled (4) · Urban Working Poor (4)

Each profile runs through the live rule engine and produces
expected outputs: eligible schemes, benefits, missing docs, welfare score.

Run: python3 generate_profiles.py
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict
from enum import Enum

# ── Engine (inline, mirrors engine/*.py) ─────────────────────────────────────

DATA = Path(__file__).parent / "data"
SCHEMES   = json.load(open(DATA / "schemes.json"))
DOCS_META = json.load(open(DATA / "documents.json"))

SCHEME_IDX = {s["scheme_id"]: s for s in SCHEMES}


def evaluate_all(p: "Profile") -> list[dict]:
    results = []
    for scheme in SCHEMES:
        c = scheme["constraints"]
        if c.get("gender")         and p.gender not in c["gender"]:              continue
        if c.get("marital_status") and p.marital_status not in c["marital_status"]: continue
        if c.get("has_disability") is True and not p.has_disability:              continue
        if c.get("min_age")        and p.age < c["min_age"]:                      continue
        if c.get("max_age")        and p.age > c["max_age"]:                      continue
        if c.get("area_type")      and p.area_type != c["area_type"]:             continue
        if c.get("occupation")     and p.occupation not in c["occupation"]:       continue
        if c.get("max_monthly_income") is not None and p.monthly_income > c["max_monthly_income"]: continue
        if c.get("min_children")   and p.children_count < c["min_children"]:     continue

        avail = set(p.available_documents)
        missing = [d for d in scheme["required_documents"] if d not in avail]
        results.append({
            "scheme_id":      scheme["scheme_id"],
            "name":           scheme["name"],
            "category":       scheme["category"],
            "monthly_benefit":  scheme["monthly_benefit"],
            "annual_benefit":   scheme["annual_benefit"],
            "one_time_benefit": scheme["one_time_benefit"],
            "missing_documents": missing,
            "status": "ready" if not missing else "eligible",
            "priority": len(missing),
        })
    results.sort(key=lambda r: (r["status"] != "ready", r["priority"]))
    return results


def benefits(results):
    return {
        "monthly":  sum(r["monthly_benefit"]  for r in results),
        "annual":   sum(r["annual_benefit"]   for r in results),
        "one_time": sum(r["one_time_benefit"] for r in results),
        "total":    sum(r["annual_benefit"] + r["one_time_benefit"] for r in results),
    }


def welfare_score(results, monthly_income):
    if not results:
        return 0, "Poor"
    e_score = min(len(results) / len(SCHEMES) * 50, 50)
    total_req  = sum(len(SCHEME_IDX[r["scheme_id"]]["required_documents"]) for r in results)
    total_miss = sum(len(r["missing_documents"]) for r in results)
    doc_score  = (1 - total_miss / max(total_req, 1)) * 40
    POVERTY = 21000
    inc_score = max(0, (1 - monthly_income / POVERTY)) * 10 if monthly_income < POVERTY else 0
    score = round(min(e_score + doc_score + inc_score, 100))
    grade = (
        "Excellent" if score >= 80 else
        "Good"      if score >= 60 else
        "Fair"      if score >= 40 else
        "Poor"
    )
    return score, grade


def top_missing_docs(results):
    freq = defaultdict(list)
    for r in results:
        for d in r["missing_documents"]:
            freq[d].append(r["scheme_id"])
    return sorted(
        [{"doc_id": k, "doc_name": DOCS_META.get(k, {}).get("name", k),
          "schemes_blocked": v} for k, v in freq.items()],
        key=lambda x: len(x["schemes_blocked"]), reverse=True
    )[:4]


# ── Profile dataclass ─────────────────────────────────────────────────────────

@dataclass
class Profile:
    id: int
    name: str
    archetype: str
    age: int
    gender: str
    marital_status: str
    district: str
    area_type: str
    monthly_income: int
    occupation: str
    family_size: int
    children_count: int
    has_disability: bool
    available_documents: list
    notes: str = ""


# ── 50 Profiles ──────────────────────────────────────────────────────────────

PROFILES: list[Profile] = [

    # ─────────────────────────────────────────────────────────
    # WIDOWS (10)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=1, name="Asha Devi", archetype="widow",
        age=52, gender="Female", marital_status="Widow",
        district="Nagpur", area_type="Rural", monthly_income=6000,
        occupation="Agricultural Labor", family_size=3, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account"],
        notes="Primary demo citizen. Two school-age children, no ration card yet.",
    ),
    Profile(
        id=2, name="Savitribai Kamble", archetype="widow",
        age=45, gender="Female", marital_status="Widow",
        district="Pune", area_type="Urban", monthly_income=8000,
        occupation="Homemaker", family_size=4, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card", "income_certificate"],
        notes="Urban widow, husband died 2 years ago. Has income cert, missing death cert.",
    ),
    Profile(
        id=3, name="Meena Shinde", archetype="widow",
        age=38, gender="Female", marital_status="Widow",
        district="Nashik", area_type="Rural", monthly_income=4500,
        occupation="Agricultural Labor", family_size=2, children_count=1,
        has_disability=False,
        available_documents=["aadhaar_card"],
        notes="Young widow, minimum documents. Highest number of missing docs.",
    ),
    Profile(
        id=4, name="Radhabai Patil", archetype="widow",
        age=62, gender="Female", marital_status="Widow",
        district="Solapur", area_type="Rural", monthly_income=3000,
        occupation="Homemaker", family_size=1, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card",
                              "income_certificate", "death_certificate_spouse", "age_proof"],
        notes="Elderly widow, all key docs present. Should be fully ready for widow + senior pensions.",
    ),
    Profile(
        id=5, name="Sunita Jadhav", archetype="widow",
        age=49, gender="Female", marital_status="Widow",
        district="Amravati", area_type="Rural", monthly_income=5500,
        occupation="Agricultural Labor", family_size=5, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card"],
        notes="Large family, partial documents. MGNREGA eligible.",
    ),
    Profile(
        id=6, name="Anita Bhosle", archetype="widow",
        age=55, gender="Female", marital_status="Widow",
        district="Kolhapur", area_type="Urban", monthly_income=12000,
        occupation="Self-Employed", family_size=3, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "income_certificate"],
        notes="Income slightly above BPL — some schemes unavailable. Self-employed tailor.",
    ),
    Profile(
        id=7, name="Vimala Gaikwad", archetype="widow",
        age=41, gender="Female", marital_status="Widow",
        district="Aurangabad", area_type="Rural", monthly_income=4000,
        occupation="Agricultural Labor", family_size=3, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card", "income_certificate",
                              "death_certificate_spouse"],
        notes="Near-complete documents. One missing doc away from full readiness.",
    ),
    Profile(
        id=8, name="Pushpa Thakare", archetype="widow",
        age=67, gender="Female", marital_status="Widow",
        district="Nagpur", area_type="Rural", monthly_income=2500,
        occupation="Homemaker", family_size=1, children_count=0,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "age_proof",
                              "disability_certificate", "ration_card"],
        notes="Elderly disabled widow. Triple overlap: widow + senior + disability pensions.",
    ),
    Profile(
        id=9, name="Lata More", archetype="widow",
        age=33, gender="Female", marital_status="Widow",
        district="Pune", area_type="Urban", monthly_income=7000,
        occupation="Private Employee", family_size=2, children_count=1,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "income_certificate",
                              "child_birth_certificate"],
        notes="Young urban widow, employed. Has girl child — Sukanya Samriddhi eligible.",
    ),
    Profile(
        id=10, name="Kalavati Raut", archetype="widow",
        age=58, gender="Female", marital_status="Widow",
        district="Chandrapur", area_type="Rural", monthly_income=0,
        occupation="Homemaker", family_size=2, children_count=1,
        has_disability=False,
        available_documents=["aadhaar_card"],
        notes="Destitute widow, zero income. Minimum docs — maximum need.",
    ),

    # ─────────────────────────────────────────────────────────
    # FARMERS (10)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=11, name="Ramrao Deshmukh", archetype="farmer",
        age=48, gender="Male", marital_status="Married",
        district="Wardha", area_type="Rural", monthly_income=9000,
        occupation="Farmer", family_size=5, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "land_document", "farmer_id"],
        notes="Cotton farmer. Has all farmer docs. PM Kisan should be ready.",
    ),
    Profile(
        id=12, name="Bhagwan Yadav", archetype="farmer",
        age=55, gender="Male", marital_status="Married",
        district="Latur", area_type="Rural", monthly_income=6000,
        occupation="Farmer", family_size=6, children_count=4,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account"],
        notes="Drought-affected farmer. Land doc and farmer ID missing.",
    ),
    Profile(
        id=13, name="Shankar Kulkarni", archetype="farmer",
        age=62, gender="Male", marital_status="Married",
        district="Satara", area_type="Rural", monthly_income=8000,
        occupation="Farmer", family_size=4, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "land_document",
                              "farmer_id", "ration_card", "age_proof"],
        notes="Senior farmer. Eligible for PM Kisan + senior pension overlap.",
    ),
    Profile(
        id=14, name="Govinda Wankhede", archetype="farmer",
        age=35, gender="Male", marital_status="Married",
        district="Buldana", area_type="Rural", monthly_income=5000,
        occupation="Farmer", family_size=4, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "land_document"],
        notes="Young marginal farmer. Missing farmer ID — easy to fix.",
    ),
    Profile(
        id=15, name="Nandabai Khandare", archetype="farmer",
        age=44, gender="Female", marital_status="Married",
        district="Yavatmal", area_type="Rural", monthly_income=7000,
        occupation="Farmer", family_size=5, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card",
                              "land_document", "farmer_id", "bpl_card"],
        notes="Female farmer with BPL card. PM Ujjwala + PM Kisan both applicable.",
    ),
    Profile(
        id=16, name="Vishnu Pawar", archetype="farmer",
        age=70, gender="Male", marital_status="Married",
        district="Osmanabad", area_type="Rural", monthly_income=4000,
        occupation="Farmer", family_size=3, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "land_document",
                              "farmer_id", "age_proof", "ration_card", "income_certificate"],
        notes="Elderly farmer. PM Kisan + senior pension + Annapurna food scheme.",
    ),
    Profile(
        id=17, name="Mahadev Salve", archetype="farmer",
        age=40, gender="Male", marital_status="Single",
        district="Nandurbar", area_type="Rural", monthly_income=5500,
        occupation="Farmer", family_size=2, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card"],
        notes="Tribal area farmer. Minimal documents — most schemes blocked.",
    ),
    Profile(
        id=18, name="Shobha Nimkar", archetype="farmer",
        age=52, gender="Female", marital_status="Married",
        district="Jalgaon", area_type="Rural", monthly_income=11000,
        occupation="Farmer", family_size=6, children_count=4,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "land_document",
                              "farmer_id", "ration_card", "income_certificate"],
        notes="Large family farmer. Income slightly above some scheme limits.",
    ),
    Profile(
        id=19, name="Pandurang Ingole", archetype="farmer",
        age=58, gender="Male", marital_status="Married",
        district="Nagpur", area_type="Rural", monthly_income=7500,
        occupation="Farmer", family_size=4, children_count=2,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "land_document",
                              "farmer_id", "disability_certificate", "income_certificate"],
        notes="Farmer with disability. PM Kisan + disability pension overlap.",
    ),
    Profile(
        id=20, name="Tulsiram Gawande", archetype="farmer",
        age=30, gender="Male", marital_status="Married",
        district="Akola", area_type="Rural", monthly_income=8000,
        occupation="Farmer", family_size=3, children_count=1,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "land_document",
                              "farmer_id", "child_birth_certificate"],
        notes="Young farmer with girl child. PM Kisan + Sukanya Samriddhi.",
    ),

    # ─────────────────────────────────────────────────────────
    # STUDENTS (8)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=21, name="Priya Meshram", archetype="student",
        age=19, gender="Female", marital_status="Single",
        district="Nagpur", area_type="Urban", monthly_income=8000,
        occupation="Student", family_size=4, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "caste_certificate",
                              "income_certificate", "marksheet"],
        notes="SC student with all scholarship docs. MahaDBT should be ready.",
    ),
    Profile(
        id=22, name="Rohit Bansode", archetype="student",
        age=22, gender="Male", marital_status="Single",
        district="Pune", area_type="Urban", monthly_income=15000,
        occupation="Student", family_size=5, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "marksheet"],
        notes="OBC student missing caste certificate. Scholarship blocked.",
    ),
    Profile(
        id=23, name="Anjali Waghmare", archetype="student",
        age=17, gender="Female", marital_status="Single",
        district="Aurangabad", area_type="Rural", monthly_income=5000,
        occupation="Student", family_size=6, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "caste_certificate",
                              "income_certificate", "marksheet"],
        notes="Dalit rural girl student. Full scholarship docs, low income family.",
    ),
    Profile(
        id=24, name="Sachin Pawar", archetype="student",
        age=20, gender="Male", marital_status="Single",
        district="Nashik", area_type="Urban", monthly_income=12000,
        occupation="Student", family_size=4, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card"],
        notes="NT student. Missing all key scholarship docs.",
    ),
    Profile(
        id=25, name="Kavitha Nair", archetype="student",
        age=24, gender="Female", marital_status="Single",
        district="Mumbai", area_type="Urban", monthly_income=20000,
        occupation="Student", family_size=3, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "caste_certificate",
                              "income_certificate", "marksheet"],
        notes="General category student near income limit. May not qualify for all schemes.",
    ),
    Profile(
        id=26, name="Deepak Sonawane", archetype="student",
        age=18, gender="Male", marital_status="Single",
        district="Kolhapur", area_type="Rural", monthly_income=6000,
        occupation="Student", family_size=5, children_count=0,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "disability_certificate",
                              "caste_certificate", "income_certificate", "marksheet"],
        notes="Disabled SC student. Scholarship + disability pension overlap.",
    ),
    Profile(
        id=27, name="Pooja Bhagat", archetype="student",
        age=16, gender="Female", marital_status="Single",
        district="Nagpur", area_type="Rural", monthly_income=4500,
        occupation="Student", family_size=7, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "caste_certificate",
                              "income_certificate", "marksheet"],
        notes="Youngest student profile. Meets minimum age for MahaDBT (16).",
    ),
    Profile(
        id=28, name="Akash Mendhe", archetype="student",
        age=28, gender="Male", marital_status="Single",
        district="Amravati", area_type="Urban", monthly_income=10000,
        occupation="Student", family_size=3, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "caste_certificate",
                              "income_certificate", "marksheet"],
        notes="Late-age student (PhD). Age 28 < 30 limit, still qualifies for MahaDBT.",
    ),

    # ─────────────────────────────────────────────────────────
    # SENIOR CITIZENS (8)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=29, name="Narayan Joshi", archetype="senior",
        age=72, gender="Male", marital_status="Married",
        district="Pune", area_type="Urban", monthly_income=5000,
        occupation="Homemaker", family_size=2, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "age_proof", "ration_card",
                              "income_certificate"],
        notes="Urban retired senior. Senior pension + Annapurna food scheme.",
    ),
    Profile(
        id=30, name="Champabai Borade", archetype="senior",
        age=68, gender="Female", marital_status="Widow",
        district="Satara", area_type="Rural", monthly_income=0,
        occupation="Homemaker", family_size=1, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "age_proof", "ration_card",
                              "income_certificate", "death_certificate_spouse"],
        notes="Elderly widow with zero income. Triple benefit: widow + senior + Annapurna.",
    ),
    Profile(
        id=31, name="Vithal Waghchoure", archetype="senior",
        age=75, gender="Male", marital_status="Married",
        district="Latur", area_type="Rural", monthly_income=3000,
        occupation="Farmer", family_size=3, children_count=0,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "age_proof", "ration_card",
                              "income_certificate", "disability_certificate",
                              "land_document", "farmer_id"],
        notes="Elderly disabled farmer. PM Kisan + senior pension + disability pension + Annapurna.",
    ),
    Profile(
        id=32, name="Godavari Thite", archetype="senior",
        age=66, gender="Female", marital_status="Married",
        district="Nashik", area_type="Rural", monthly_income=8000,
        occupation="Homemaker", family_size=4, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "age_proof"],
        notes="Senior missing ration card and income cert — blocking most schemes.",
    ),
    Profile(
        id=33, name="Krishnarao Deshpande", archetype="senior",
        age=80, gender="Male", marital_status="Widower",
        district="Nagpur", area_type="Urban", monthly_income=4000,
        occupation="Homemaker", family_size=1, children_count=0,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "age_proof", "ration_card",
                              "income_certificate", "disability_certificate"],
        notes="Very elderly disabled widower. Maximum welfare need, high scheme overlap.",
    ),
    Profile(
        id=34, name="Sindhu Parkar", archetype="senior",
        age=63, gender="Female", marital_status="Married",
        district="Raigad", area_type="Rural", monthly_income=6000,
        occupation="Agricultural Labor", family_size=3, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card",
                              "income_certificate", "age_proof"],
        notes="Working senior. MGNREGA + senior pension overlap.",
    ),
    Profile(
        id=35, name="Balwant Bhalerao", archetype="senior",
        age=61, gender="Male", marital_status="Married",
        district="Solapur", area_type="Rural", monthly_income=20500,
        occupation="Self-Employed", family_size=4, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "age_proof", "income_certificate"],
        notes="Senior just over income threshold. Fewer schemes available.",
    ),
    Profile(
        id=36, name="Tarabai Salunke", archetype="senior",
        age=69, gender="Female", marital_status="Widow",
        district="Beed", area_type="Rural", monthly_income=0,
        occupation="Homemaker", family_size=2, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card"],
        notes="Destitute elderly widow. Minimum documents — urgent intervention needed.",
    ),

    # ─────────────────────────────────────────────────────────
    # AGRICULTURAL LABOR (6)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=37, name="Mukesh Rathod", archetype="agri_labor",
        age=34, gender="Male", marital_status="Married",
        district="Dhule", area_type="Rural", monthly_income=7000,
        occupation="Agricultural Labor", family_size=5, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card", "job_card"],
        notes="MGNREGA job card holder. Ready for employment scheme immediately.",
    ),
    Profile(
        id=38, name="Sushma Sonar", archetype="agri_labor",
        age=28, gender="Female", marital_status="Married",
        district="Wardha", area_type="Rural", monthly_income=5000,
        occupation="Agricultural Labor", family_size=4, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card", "bpl_card"],
        notes="Young female laborer with BPL card. PM Ujjwala + Ayushman eligible.",
    ),
    Profile(
        id=39, name="Kiran Chavhan", archetype="agri_labor",
        age=45, gender="Male", marital_status="Married",
        district="Nanded", area_type="Rural", monthly_income=6500,
        occupation="Agricultural Labor", family_size=6, children_count=4,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account"],
        notes="Large family, minimum docs. Multiple schemes blocked.",
    ),
    Profile(
        id=40, name="Rekha Nandurkar", archetype="agri_labor",
        age=39, gender="Female", marital_status="Married",
        district="Hingoli", area_type="Rural", monthly_income=4000,
        occupation="Agricultural Labor", family_size=5, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card", "bpl_card",
                              "income_certificate", "child_birth_certificate", "job_card"],
        notes="Well-documented female laborer. Sukanya + MGNREGA + Ujjwala all accessible.",
    ),
    Profile(
        id=41, name="Datta Shirsat", archetype="agri_labor",
        age=50, gender="Male", marital_status="Married",
        district="Parbhani", area_type="Rural", monthly_income=5500,
        occupation="Agricultural Labor", family_size=4, children_count=2,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "disability_certificate",
                              "ration_card", "income_certificate"],
        notes="Disabled agricultural laborer. Disability pension + MGNREGA.",
    ),
    Profile(
        id=42, name="Yamuna Pawade", archetype="agri_labor",
        age=22, gender="Female", marital_status="Single",
        district="Osmanabad", area_type="Rural", monthly_income=3500,
        occupation="Agricultural Labor", family_size=3, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card",
                              "bpl_card", "job_card"],
        notes="Young single female laborer. PMSBY insurance should be ready.",
    ),

    # ─────────────────────────────────────────────────────────
    # PERSONS WITH DISABILITY (4)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=43, name="Suresh Ambhore", archetype="disabled",
        age=38, gender="Male", marital_status="Married",
        district="Pune", area_type="Urban", monthly_income=9000,
        occupation="Self-Employed", family_size=3, children_count=1,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "disability_certificate",
                              "income_certificate", "child_birth_certificate"],
        notes="Disabled self-employed person with girl child. Disability pension + Sukanya.",
    ),
    Profile(
        id=44, name="Nirmala Jagtap", archetype="disabled",
        age=29, gender="Female", marital_status="Single",
        district="Mumbai", area_type="Urban", monthly_income=6000,
        occupation="Private Employee", family_size=2, children_count=0,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "disability_certificate"],
        notes="Young disabled woman. Missing income cert — blocking pension.",
    ),
    Profile(
        id=45, name="Pramod Nimse", archetype="disabled",
        age=55, gender="Male", marital_status="Married",
        district="Akola", area_type="Rural", monthly_income=5000,
        occupation="Homemaker", family_size=4, children_count=2,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "disability_certificate",
                              "income_certificate", "ration_card"],
        notes="Disabled rural resident. Disability pension + Ayushman + PMSBY.",
    ),
    Profile(
        id=46, name="Geeta Landge", archetype="disabled",
        age=42, gender="Female", marital_status="Widow",
        district="Yavatmal", area_type="Rural", monthly_income=3500,
        occupation="Homemaker", family_size=2, children_count=1,
        has_disability=True,
        available_documents=["aadhaar_card", "bank_account", "disability_certificate",
                              "ration_card", "income_certificate", "death_certificate_spouse"],
        notes="Disabled widow. Maximum overlap: widow pension + disability pension.",
    ),

    # ─────────────────────────────────────────────────────────
    # URBAN WORKING POOR (4)
    # ─────────────────────────────────────────────────────────

    Profile(
        id=47, name="Santosh Kadam", archetype="urban_poor",
        age=32, gender="Male", marital_status="Married",
        district="Pune", area_type="Urban", monthly_income=11000,
        occupation="Private Employee", family_size=4, children_count=2,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card",
                              "income_certificate", "child_birth_certificate"],
        notes="Urban factory worker. Ayushman + PMSBY + Sukanya all within reach.",
    ),
    Profile(
        id=48, name="Shalini Mhatre", archetype="urban_poor",
        age=26, gender="Female", marital_status="Married",
        district="Thane", area_type="Urban", monthly_income=9500,
        occupation="Private Employee", family_size=3, children_count=1,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "income_certificate",
                              "child_birth_certificate"],
        notes="Young urban working mother. Missing ration card — blocks Ayushman.",
    ),
    Profile(
        id=49, name="Rahul Gaikwad", archetype="urban_poor",
        age=24, gender="Male", marital_status="Single",
        district="Nashik", area_type="Urban", monthly_income=8000,
        occupation="Self-Employed", family_size=1, children_count=0,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account"],
        notes="Young single urban worker. PMSBY only ready scheme. Minimal household.",
    ),
    Profile(
        id=50, name="Sunanda Wagh", archetype="urban_poor",
        age=36, gender="Female", marital_status="Married",
        district="Aurangabad", area_type="Urban", monthly_income=10000,
        occupation="Homemaker", family_size=5, children_count=3,
        has_disability=False,
        available_documents=["aadhaar_card", "bank_account", "ration_card",
                              "income_certificate", "bpl_card", "child_birth_certificate"],
        notes="Urban homemaker with BPL card. PM Ujjwala + Ayushman + Sukanya eligible.",
    ),
]


# ── Run all profiles through the engine ──────────────────────────────────────

def process_profile(p: Profile) -> dict:
    results   = evaluate_all(p)
    b         = benefits(results)
    score, grade = welfare_score(results, p.monthly_income)
    missing   = top_missing_docs(results)
    ready     = [r for r in results if r["status"] == "ready"]

    return {
        "profile": {
            "id": p.id,
            "name": p.name,
            "archetype": p.archetype,
            "age": p.age,
            "gender": p.gender,
            "marital_status": p.marital_status,
            "district": p.district,
            "area_type": p.area_type,
            "monthly_income": p.monthly_income,
            "occupation": p.occupation,
            "family_size": p.family_size,
            "children_count": p.children_count,
            "has_disability": p.has_disability,
            "available_documents": p.available_documents,
            "notes": p.notes,
        },
        "output": {
            "welfare_score": score,
            "welfare_grade": grade,
            "schemes_evaluated": len(SCHEMES),
            "schemes_eligible": len(results),
            "schemes_ready": len(ready),
            "monthly_benefit_inr": b["monthly"],
            "annual_benefit_inr":  b["annual"],
            "one_time_benefit_inr": b["one_time"],
            "total_annual_value_inr": b["total"],
            "eligible_schemes": [
                {
                    "scheme_id": r["scheme_id"],
                    "name": r["name"],
                    "category": r["category"],
                    "monthly_benefit": r["monthly_benefit"],
                    "one_time_benefit": r["one_time_benefit"],
                    "status": r["status"],
                    "missing_documents": r["missing_documents"],
                }
                for r in results
            ],
            "top_missing_documents": missing,
        },
    }


def main():
    all_outputs = []

    for p in PROFILES:
        out = process_profile(p)
        all_outputs.append(out)

    # ── Write full JSON ───────────────────────────────────────────────────────
    out_path = Path(__file__).parent / "data" / "citizen_profiles.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_outputs, f, ensure_ascii=False, indent=2)

    # ── Print summary table ───────────────────────────────────────────────────
    archetypes = {}
    for o in all_outputs:
        arch = o["profile"]["archetype"]
        if arch not in archetypes:
            archetypes[arch] = []
        archetypes[arch].append(o)

    print("=" * 90)
    print(f"{'JANHI T — 50 CITIZEN PROFILES — ENGINE OUTPUT':^90}")
    print("=" * 90)
    print(f"{'#':<4} {'Name':<22} {'Arch':<14} {'Score':<8} {'Eligible':<10} {'Ready':<7} {'Monthly ₹':<12} {'Annual ₹'}")
    print("-" * 90)

    for arch_name, group in archetypes.items():
        print(f"\n  ── {arch_name.upper().replace('_', ' ')} ──")
        for o in group:
            p  = o["profile"]
            op = o["output"]
            print(
                f"  {p['id']:<3} {p['name']:<22} {p['archetype']:<14} "
                f"{op['welfare_score']:<8} {op['schemes_eligible']:<10} "
                f"{op['schemes_ready']:<7} {op['monthly_benefit_inr']:>10,}  "
                f"{op['total_annual_value_inr']:>10,}"
            )

    # ── Aggregate statistics ──────────────────────────────────────────────────
    scores  = [o["output"]["welfare_score"]        for o in all_outputs]
    totals  = [o["output"]["total_annual_value_inr"] for o in all_outputs]
    monthlies = [o["output"]["monthly_benefit_inr"]  for o in all_outputs]

    print("\n" + "=" * 90)
    print("AGGREGATE STATISTICS")
    print("=" * 90)
    print(f"  Total profiles generated : {len(all_outputs)}")
    print(f"  Avg welfare score        : {sum(scores) / len(scores):.1f}")
    print(f"  Min / Max welfare score  : {min(scores)} / {max(scores)}")
    print(f"  Avg monthly benefit      : ₹{sum(monthlies) / len(monthlies):,.0f}")
    print(f"  Avg annual value         : ₹{sum(totals) / len(totals):,.0f}")
    print(f"  Total benefits modelled  : ₹{sum(totals):,.0f}")

    # Most common missing doc
    all_missing_docs = []
    for o in all_outputs:
        for r in o["output"]["eligible_schemes"]:
            all_missing_docs.extend(r["missing_documents"])

    doc_freq = defaultdict(int)
    for d in all_missing_docs:
        doc_freq[d] += 1

    print("\n  Most-missing documents (across 50 profiles):")
    for doc_id, count in sorted(doc_freq.items(), key=lambda x: x[1], reverse=True)[:6]:
        doc_name = DOCS_META.get(doc_id, {}).get("name", doc_id)
        print(f"    {doc_name:<40} {count:>4}x missing")

    # Most matched schemes
    scheme_hits = defaultdict(int)
    for o in all_outputs:
        for r in o["output"]["eligible_schemes"]:
            scheme_hits[r["scheme_id"]] += 1

    print("\n  Most-eligible schemes (across 50 profiles):")
    for sid, count in sorted(scheme_hits.items(), key=lambda x: x[1], reverse=True)[:6]:
        sname = SCHEME_IDX[sid]["name"]
        print(f"    {sname:<45} {count:>3} / 50 profiles")

    print(f"\n  Output saved → {out_path}")
    print("=" * 90)

    return all_outputs


if __name__ == "__main__":
    main()
