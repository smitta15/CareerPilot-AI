from pydantic import BaseModel
import logging

from app.services.models import agent_llm
from app.utils.retry import retry_llm

logger = logging.getLogger("careerpilot")


class SearchQuery(BaseModel):
    role: str
    skills: list[str] = []
    location: str | None = None


# Prefer structured output but be resilient to model/provider differences
try:
    structured_llm = agent_llm.with_structured_output(SearchQuery)
except Exception:
    structured_llm = None


def generate_search_query(user_query, profile):

    prompt = f"""
You are an AI career assistant.

User Request:
{user_query}

Candidate Skills:
{profile.get("skills", [])}

Extract the job search information.

Return:

- role: Primary job role
- skills: Important technical skills
- location: Location if mentioned, otherwise null

Examples:

User: Backend Developer Java Spring Boot
Output:
role="Backend Developer"
skills=["Java","Spring Boot"]
location=null

User: Data Scientist Hyderabad Python
Output:
role="Data Scientist"
skills=["Python"]
location="Hyderabad"

Return only the structured output.
"""

    # Try structured output first (more reliable parsing). If it fails,
    # fall back to a plain text response and use the raw content.
    if structured_llm is not None:
        try:
            result = retry_llm(lambda: structured_llm.invoke(prompt))
            return result
        except Exception as e:
            logger.warning("structured search query generation failed: %s", e)

    if agent_llm is not None:
        try:
            response = retry_llm(lambda: agent_llm.invoke(prompt))
            content = getattr(response, 'content', None) or response
            query = str(content).strip().splitlines()[0]
            if query.startswith('"') and query.endswith('"'):
                query = query[1:-1]
            return SearchQuery(role=query, skills=profile.get("skills", []))
        except Exception as e:
            logger.exception("Failed to generate search query: %s", e)

    return SearchQuery(role=user_query, skills=profile.get("skills", []))
