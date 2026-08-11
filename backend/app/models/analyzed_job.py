"""Typed response model for analyzed jobs."""

from pydantic import BaseModel
from typing import Dict, Optional


class AnalyzedJob(BaseModel):
    """Response model for job analysis results."""

    job: Dict
    match_score: int
    match_reason: str
    company_report: Dict
    skill_gap: Dict
    tailored_resume: str
    decision: Optional[Dict] = None
    status: str