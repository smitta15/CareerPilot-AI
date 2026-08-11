from pydantic import BaseModel, Field
from typing import Optional


class JobRequest(BaseModel):

    user_query: str


class ResumeRequest(BaseModel):

    thread_id: str

    approved: bool


class AnalyzeRequest(BaseModel):
    """Request to analyze a specific job within an existing thread.

    Either provide thread_id (to resume a previous run) and optional job_index
    (index into shortlisted_jobs) or provide only thread_id to analyze the
    currently selected job.
    """

    thread_id: str
    job_index: Optional[int] = Field(default=None, ge=0)


class ApplyRequest(BaseModel):
    """Request to apply to the selected job in a thread."""

    thread_id: str
    approved: bool = True
