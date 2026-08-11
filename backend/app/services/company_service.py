from app.services.models import agent_llm
from app.models.company_model import CompanyReport
from app.utils.retry import retry_llm

try:
    structured_llm = agent_llm.with_structured_output(CompanyReport) if agent_llm else None
except Exception:
    structured_llm = None


def research_company(job):
    if structured_llm is None:
        skills = job.get("skills", []) or []
        return {
            "overview": f"{job.get('company', 'The company')} is hiring for {job.get('title', 'this role')}.",
            "tech_stack": skills,
            "interview_process": ["Resume screening", "Technical interview", "Hiring discussion"],
            "hiring_focus": ["Relevant project experience", "Core technical skills", "Clear communication"],
            "ats_keywords": skills + [job.get("title", "internship")],
        }

    prompt = f"""
You are an AI career advisor.

Research this company.

Company:
{job["company"]}

Role:
{job["title"]}

Job Description:
{job["description"]}

Generate:

1. Company overview

2. Technologies commonly used

3. Interview process

4. Hiring focus

5. ATS keywords
"""

    result = retry_llm(
        lambda: structured_llm.invoke(prompt)
    )

    return result.model_dump()
