from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scheme import Scheme
from app.schemas.scheme import SchemeCreate, SchemeOut

router = APIRouter(prefix="/schemes", tags=["schemes"])


@router.get("", response_model=list[SchemeOut])
def list_schemes(db: Session = Depends(get_db)):
    return db.query(Scheme).all()


@router.post("", response_model=SchemeOut, status_code=201)
def create_scheme(payload: SchemeCreate, db: Session = Depends(get_db)):
    """Lets an admin add/edit rule rows without touching code —
    this is the 'rule table' the eligibility engine reads from."""
    scheme = Scheme(**payload.model_dump())
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    return scheme
