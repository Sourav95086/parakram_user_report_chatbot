from pydantic import BaseModel
from typing import Literal


class Reporter(BaseModel):
    name: str
    phone: str


class IssueOutput(BaseModel):

    issue_category: str
    issue_weight: float
    estimated_cost_range: str
    issue_description: str

    reported_by: Reporter

    issue_location: str

    latitude: float
    longitude: float

    evidence: str | None = None