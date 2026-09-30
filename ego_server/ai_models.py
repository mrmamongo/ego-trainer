"""Validated tutoring, response review and billing contracts."""

from decimal import Decimal
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class AccessUpdate(BaseModel):
    enabled: bool
    defense_required: bool = True


class CreditRequest(BaseModel):
    amount_usd: Decimal = Field(gt=0, le=10000, decimal_places=6)
    request_id: str = Field(min_length=1, max_length=80)


class AIAccount(BaseModel):
    student_id: str
    enabled: bool
    defense_required: bool
    available: bool
    reason: str
    balance_usd: str
    reserved_usd: str
    spent_usd: str


class SessionCreate(BaseModel):
    task_id: str = Field(min_length=1, max_length=100)
    mode: Literal["hint", "explain", "defend"] = "hint"
    student_code: str = Field(default="", max_length=24000)
    submission_id: str | None = Field(default=None, max_length=80)


class MessageRequest(BaseModel):
    student_code: str | None = Field(default=None, max_length=24000)
    text: str = Field(default="", max_length=4000)
    request_id: str = Field(default_factory=lambda: uuid4().hex, min_length=1, max_length=80)


class TutorDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reply: str = Field(min_length=1, max_length=12000)
    step_passed: StrictBool = False
    evidence: str = Field(default="", max_length=1000)


class GuardVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allow: StrictBool
    reason: str = Field(min_length=1, max_length=1000)
