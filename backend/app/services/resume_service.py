from pathlib import Path

from app.services.models import planner_llm
from app.utils.retry import retry_llm

MASTER_RESUME = Path(__file__).resolve().parents[1] / "resumes" / "master_resume.md"


def tailor_resume(job, profile):

    resume = MASTER_RESUME.read_text(encoding="utf-8")

    if planner_llm is None:
        skills = ", ".join(profile.get("skills", []))
        job_skills = ", ".join(job.get("skills", []))
        return f"""{resume}

## Target Role

{job.get("title", "Internship")} at {job.get("company", "the company")}

## Tailoring Notes

- Emphasize candidate skills: {skills or "relevant project experience"}.
- Align with job requirements: {job_skills or "the listed role requirements"}.
- Reference the job description when preparing the final application.
"""

    prompt = f"""
Tailor the following resume for this job.

JOB

{job}

RESUME

{resume}

Return only the updated resume.
"""

    response = retry_llm(lambda: planner_llm.invoke(prompt))

    return response.content
