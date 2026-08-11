from app.services.llm import llm


def analyze_skill_gap(profile, job):
    candidate_skills = {skill.lower() for skill in profile.get("skills", [])}
    job_skills = job.get("skills", []) or []

    if llm is None:
        matched = [skill for skill in job_skills if skill.lower() in candidate_skills]
        missing = [skill for skill in job_skills if skill.lower() not in candidate_skills]
        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "priority": missing[:3],
        }

    prompt = f"""
Compare this profile

{profile}

with this job

{job}

Return:

Skills already known

Missing skills

Learning roadmap

Return markdown.
"""

    response = llm.invoke(prompt)

    return response.content
