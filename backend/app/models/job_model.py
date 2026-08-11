from pydantic import BaseModel
from typing import List


class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    skills: List[str]
    apply_link: str