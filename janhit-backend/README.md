# JanHit Backend

FastAPI + PostgreSQL backend for the JanHit frontend (frontline welfare worker tool).
Deterministic rule-based eligibility engine — no AI/LLM decisions.

## Quickest start (no Docker, no Postgres install — SQLite)
```
pip install -r requirements.txt
python -m app.seed     # creates janhit.db automatically and seeds the 4 demo schemes
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

SQLite is the default (`DATABASE_URL=sqlite:///./janhit.db`). Tables are
created automatically on startup in this mode — no Alembic step needed.

## Production (Postgres)
Set `DATABASE_URL=postgresql://user:pass@host:5432/janhit` in `.env`, then:
```
alembic upgrade head
python -m app.seed
uvicorn app.main:app
```
Postgres always goes through Alembic migrations (`alembic/versions/0001_initial_schema.py`).

## Docker (optional)
```
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.seed
```

## Core flow
Assessment (POST /assessments) → Eligibility (POST /assessments/{id}/eligibility)
→ Action Plan (POST /cases/{id}/action-plan) → Share (POST /cases/{id}/share)
→ Public record (GET /citizen-record/{token})

Cases list (workspace): GET /cases?status=pending
District stats: GET /analytics/district

## Note on auth
JWT auth is intentionally deferred (per product decision) — `users` table
exists, but no endpoint currently requires a token. All routes are open.

