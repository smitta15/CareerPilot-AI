from app.models.report_model import FinalReport
from app.services.models import report_llm
from app.utils.retry import retry_llm
import logging

logger = logging.getLogger("careerpilot")

# Try to create structured LLM, but be resilient if provider doesn't support it
try:
    structured_llm = report_llm.with_structured_output(FinalReport) if report_llm else None
except Exception:
    structured_llm = None


def generate_report(state: dict):

    user_query = state.get("user_query", "")
    selected_job = state.get("selected_job", {})
    company_report = state.get("company_report", {})
    skill_gap = state.get("skill_gap", {})
    tailored_resume = state.get("tailored_resume", "")
    match_score = state.get("match_score", 0)
    applications = state.get("applications", [])

    prompt = f"""
You are the Report Agent of CareerPilot.

Generate a concise final report for the completed workflow.

User Query:
{user_query}

Selected Job:
{selected_job}

Company Report:
{company_report}

Skill Gap:
{skill_gap}

Resume:
{tailored_resume}

Match Score:
{match_score}

Applications:
{applications}

Return:

- selected_job
- company
- match_summary
- company_summary
- skill_gap_summary
- resume_summary
- application_status
- next_steps
"""

    # Prefer structured output when available
    if structured_llm is not None:
        try:
            report = retry_llm(lambda: structured_llm.invoke(prompt))
            return report.model_dump()
        except Exception as e:
            logger.warning("structured report generation failed: %s", e)

    fallback = {
        "selected_job": selected_job or {},
        "company": (selected_job.get('company') if isinstance(selected_job, dict) else ''),
        "match_summary": f"Match score: {match_score}",
        "company_summary": company_report.get('overview', '') if isinstance(company_report, dict) else str(company_report),
        "skill_gap_summary": skill_gap if isinstance(skill_gap, (str, dict)) else str(skill_gap),
        "resume_summary": (tailored_resume[:100] + '...') if tailored_resume else '',
        "application_status": ', '.join([a.get('status', '') for a in applications]) if isinstance(applications, list) else str(applications),
        "next_steps": [],
    }

    if report_llm is None:
        return fallback

    # Fallback: plain text generation and best-effort parsing
    try:
        response = retry_llm(lambda: report_llm.invoke(prompt))
        content = getattr(response, 'content', None) or str(response)
        fallback["raw_summary"] = content
        return fallback
    except Exception as e:
        logger.exception("Failed to generate report: %s", e)
        return fallback
