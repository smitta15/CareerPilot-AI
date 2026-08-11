from pydantic import BaseModel
from typing import List, Dict, Any


class Task(BaseModel):

    agent: str

    input: Dict[str, Any]

    status: str


class ExecutionPlan(BaseModel):

    tasks: List[Task]