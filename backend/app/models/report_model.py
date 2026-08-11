from pydantic import BaseModel
from typing import List


class FinalReport(BaseModel):

    selected_job: str

    company: str

    match_summary: str

    company_summary: str

    skill_gap_summary: str

    resume_summary: str

    application_status: str

    next_steps: List[str]