from pydantic import BaseModel
from typing import List


class CompanyReport(BaseModel):
    overview: str
    tech_stack: List[str]
    interview_process: List[str]
    hiring_focus: List[str]
    ats_keywords: List[str]