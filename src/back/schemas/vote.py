from typing import Literal

from pydantic import BaseModel


class VoteRequest(BaseModel):
    value: Literal[-1, 0, 1]


class VoteResponse(BaseModel):
    score: int
    userVote: int | None
