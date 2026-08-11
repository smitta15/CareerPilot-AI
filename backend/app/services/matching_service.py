from app.services.models import agent_llm
from app.utils.retry import retry_llm
from app.models.match_model import RankingResult, RankedJob

try:
    structured_llm = agent_llm.with_structured_output(RankingResult) if agent_llm else None
except Exception:
    structured_llm = None


def rank_jobs(profile,user_query, jobs):
    if structured_llm is None:
        return [
            RankedJob(
                index=index,
                score=int(job.get("base_score", 0)),
                reason="Ranked using deterministic role and skill matching.",
            )
            for index, job in enumerate(jobs)
        ]

    prompt = f"""
You are an expert technical recruiter.

The MOST IMPORTANT requirement is matching the user's requested role.

Requested Role:
{user_query}

Candidate Skills:
{profile["skills"]}

Instructions:

1. Give HIGH scores only to jobs matching the requested role.
2. Penalize unrelated roles heavily.
3. Skills matter, but role match matters even more.
4. Ignore senior management positions unless explicitly requested.
5. Do not rank Project Manager, HR, Sales, Marketing, or Network roles highly if the user requested Software Engineer.
6. Return a score between 0 and 100.

"""

    for i, job in enumerate(jobs):

        prompt += f"""
Job {i}

Title: {job["title"]}

Company: {job["company"]}

Skills:
{job["skills"]}

Description:
{job["description"][:1500]}
"""

    prompt += """

For every job return:

index
score (0-100)
reason (1 sentence)

Rank every job.
"""

    result = retry_llm(
        lambda: structured_llm.invoke(prompt)
    )

    return result.rankings
