from pydantic import BaseModel
from typing import List


class MatchResult(BaseModel):
    score: int
    reason: str


class RankedJob(BaseModel):
    index: int
    score: int
    reason: str


class RankingResult(BaseModel):
    rankings: List[RankedJob]