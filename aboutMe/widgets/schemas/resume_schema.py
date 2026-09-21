from typing import List

from pydantic import BaseModel

from .education_schema import EducationSchema
from .experience_schema import ExperienceSchema


class ResumeSchema(BaseModel):
    experience: List[ExperienceSchema]
    education: List[EducationSchema]
