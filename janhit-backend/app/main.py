from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine, is_sqlite
from app import models  # noqa: registers all models on Base before create_all
from app.routers import (
    beneficiaries, cases, assessments, eligibility,
    action_plans, shareable_links, analytics, schemes,
)

app = FastAPI(title="JanHit API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(beneficiaries.router)
app.include_router(cases.router)
app.include_router(assessments.router)
app.include_router(eligibility.router)
app.include_router(action_plans.router)
app.include_router(shareable_links.router)
app.include_router(analytics.router)
app.include_router(schemes.router)


@app.on_event("startup")
def on_startup():
    # SQLite dev mode: create tables directly, no Alembic needed to get
    # started. Postgres (prod) always goes through `alembic upgrade head`
    # so schema changes stay tracked in migrations.
    if is_sqlite:
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
