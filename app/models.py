# app/models.py
from pydantic import BaseModel
from typing import List


class ScoreRequest(BaseModel):
    transcript: str
    duration_sec: float  # audio length in seconds


class CriterionResult(BaseModel):
    criterion: str
    max_score: float
    score: float
    detail: str


class ScoreResponse(BaseModel):
    overall_score: float           # final 0–100 score
    base_rubric_score: float       # sum of classical rubric scores (0–100)
    semantic_score_0_10: float     # semantic score (0–10)
    max_score: float               # always 100
    words: int
    duration_sec: float
    wpm: float
    criteria: List[CriterionResult]
