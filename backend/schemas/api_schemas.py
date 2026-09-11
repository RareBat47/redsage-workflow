from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    target_type: str = "web_app"


class ProjectBriefUpdate(BaseModel):
    text: str = Field(max_length=20_000)

class ScopeUpdate(BaseModel):
    in_scope_whitelist: List[str]
    out_of_scope_blacklist: List[str] = []
    max_rate_limit: int = Field(default=10, ge=1, le=1000)


class ScopeAmend(BaseModel):
    additional_targets: List[str] = Field(min_length=1)
    authorized_by: str = Field(min_length=1, max_length=200)
    rationale: str = Field(min_length=10, max_length=5_000)


class TaskStateUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=64)
    justification: Optional[str] = Field(default=None, max_length=5_000)

class EvidenceSubmit(BaseModel):
    raw_content: str = Field(min_length=1, max_length=2_000_000)

class FindingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    severity: str = "MEDIUM"
    description: str = ""
    reproduction_steps: str = ""
    remediation: Optional[str] = None
    affected_asset: Optional[str] = None
    # Optional for DRAFT findings; CONFIRMED findings require valid evidence.
    evidence_id: Optional[str] = None

class FindingConfirm(BaseModel):
    evidence_id: str = Field(min_length=1)
    title: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    reproduction_steps: Optional[str] = None
    remediation: Optional[str] = None
    affected_asset: Optional[str] = None

class MentorAsk(BaseModel):
    mode: Literal["teach", "guide", "verify", "summarize"]
    user_message: str = Field(min_length=1, max_length=4000)
    target_host: Optional[str] = None
    step_id: Optional[str] = None


class TaskStepCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    objective: str = Field(default="", max_length=5_000)
    why_it_matters: str = Field(default="", max_length=5_000)
    completion_criteria: str = Field(default="", max_length=5_000)
    expected_evidence_type: str = Field(default="TERMINAL_LOG", max_length=200)


class TaskStepUpdate(TaskStepCreate):
    order_index: Optional[int] = Field(default=None, ge=1)


class WorkflowApply(BaseModel):
    mode: Literal["replace", "merge"]
    draft: dict
