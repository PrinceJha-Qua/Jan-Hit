from typing import List
from pydantic import BaseModel


class TopScheme(BaseModel):
    name: str
    count: int


class MonthlyTrend(BaseModel):
    month: str
    cases: int


class DistrictStatsOut(BaseModel):
    total_cases: int
    pending_cases: int
    completed_this_month: int
    schemes_disbursed: int
    top_schemes: List[TopScheme]
    monthly_trend: List[MonthlyTrend]
