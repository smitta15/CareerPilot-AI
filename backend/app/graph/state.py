"""
State definition for CareerPilot AI LangGraph workflow.

Defines all fields that are shared across agents during execution.
Uses TypedDict for type safety and clarity.
"""

from typing import TypedDict, Optional, Any


class CareerPilotState(TypedDict, total=False):
    """
    Shared state across all LangGraph agents.

    Fields marked as Optional can be missing or None.
    All list/dict fields are initialized as empty to avoid mutable default issues.
    """

    # ==================== User & Query ====================
    user_query: str
    search_query: str
    execution_plan: list
    current_step: int

    # ==================== Profile & Preferences ====================
    profile: dict

    # ==================== Search Results ====================
    opportunities: list
    shortlisted_jobs: list
    analyzed_jobs: list

    # ==================== Job Selection & Analysis ====================
    selected_job: Optional[dict]
    match_score: int
    match_reason: str

    # ==================== Company & Skills ====================
    company_report: Optional[dict]
    skill_gap: Optional[dict]
    tailored_resume: Optional[str]

    # ==================== Decision & Application ====================
    approval_required: bool
    approval_reason: str
    approved: bool
    decision: Optional[dict]
    applications: list

    # ==================== Final Output ====================
    final_response: dict

    # ==================== Metadata ====================
    thread_id: Optional[str]
    error: Optional[str]