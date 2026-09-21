from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class EmploymentType(Enum):
    FULL_TIME = "Full-time"
    SELF_EMPLOYED = "Self-employed"
    FREELANCE = "Freelance"
    INTERNSHIP = "Internship"


class LocationType(Enum):
    REMOTE = "Remote"
    ONSITE = "On-site"
    HYBRID = "Hybrid"


class PositionSchema(BaseModel):
    title: str
    startDate: date
    endDate: date = date.today()
    present: bool = False
    location: Optional[str] = None
    employmentType: EmploymentType
    locationType: LocationType


class ExperienceSchema(BaseModel):
    company: str
    positions: List[PositionSchema]
