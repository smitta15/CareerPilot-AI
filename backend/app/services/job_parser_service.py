from pydantic import BaseModel
from typing import List
import re

from app.services.models import agent_llm
from app.utils.retry import retry_llm


class SkillExtraction(BaseModel):
    skills: List[str]


try:
    structured_llm = agent_llm.with_structured_output(SkillExtraction) if agent_llm else None
except Exception:
    structured_llm = None

KNOWN_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js",
    "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MongoDB",
    "Redis", "Docker", "Kubernetes", "AWS", "Git", "C++", "DSA",
    "Spring Boot", "Machine Learning",
]


def extract_skills(description: str):
    if structured_llm is None:
        text = description or ""
        return [
            skill
            for skill in KNOWN_SKILLS
            if re.search(rf"\b{re.escape(skill)}\b", text, flags=re.IGNORECASE)
        ]

    prompt = f"""
Extract only the technical skills required in this job.

Job Description:

{description}

Return only the skills.
"""

    result = retry_llm(
        lambda: structured_llm.invoke(prompt)
    )

    return result.skills
