import uuid
from sqlalchemy import Column, String, Integer, Boolean

from app.database import Base, GUID


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    district = Column(String, nullable=False)
    occupation = Column(String, nullable=False)
    annual_income = Column(Integer, nullable=False)
    is_widow = Column(Boolean, default=False)
    is_farmer = Column(Boolean, default=False)
    has_disability = Column(Boolean, default=False)
    caste = Column(String, nullable=True)
    gender = Column(String, nullable=False)  # female | male | other
