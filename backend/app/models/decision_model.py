from pydantic import BaseModel, Field
from typing import Literal, List


class Decision(BaseModel):
    decision: Literal["apply", "reject", "ask_user"]
    confidence: int = Field(default=0, ge=0, le=100)
    reason: str = ""
    recommendation: str = ""
    summary: str = ""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)