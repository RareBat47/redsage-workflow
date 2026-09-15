import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    brief = Column(Text, nullable=True)
    target_type = Column(String, nullable=False, default="web_app")
    status = Column(String, nullable=False, default="IN_PROGRESS")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    scope = relationship("Scope", back_populates="project", uselist=False, cascade="all, delete-orphan")
    phases = relationship("Phase", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="project", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="project", cascade="all, delete-orphan")
    proposals = relationship("WorkflowProposal", back_populates="project", cascade="all, delete-orphan")
    scope_amendments = relationship("ScopeAmendment", back_populates="project", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="project", cascade="all, delete-orphan")
    mentor_messages = relationship("MentorMessage", back_populates="project", cascade="all, delete-orphan")

class Scope(Base):
    __tablename__ = "scopes"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), unique=True, nullable=False)
    in_scope_whitelist = Column(Text, nullable=False)
    out_of_scope_blacklist = Column(Text, nullable=False)
    max_rate_limit = Column(Integer, default=10)
    is_locked = Column(Boolean, default=False)
    locked_at = Column(DateTime)
    project = relationship("Project", back_populates="scope")

class ScopeAmendment(Base):
    __tablename__ = "scope_amendments"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    added_targets = Column(Text, nullable=False)
    authorized_by = Column(String, nullable=False)
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project = relationship("Project", back_populates="scope_amendments")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    event_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    details = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project = relationship("Project", back_populates="audit_events")

class Phase(Base):
    __tablename__ = "phases"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    order_index = Column(Integer, nullable=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime, nullable=True)
    archived_by = Column(String, nullable=True)
    project = relationship("Project", back_populates="phases")
    tasks = relationship("Task", back_populates="phase", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    phase_id = Column(String, ForeignKey("phases.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    objective = Column(Text, nullable=False)
    command_template = Column(Text)
    status = Column(String, default="NOT_STARTED")
    priority = Column(String, default="MEDIUM")
    order_index = Column(Integer, nullable=False)
    is_ai_proposed = Column(Boolean, default=False)
    justification = Column(Text)
    is_archived = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime, nullable=True)
    archived_by = Column(String, nullable=True)
    phase = relationship("Phase", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    evidence = relationship("Evidence", back_populates="task")
    steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan")


class TaskStep(Base):
    __tablename__ = "task_steps"
    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    title = Column(String, nullable=False)
    objective = Column(Text, nullable=False, default="")
    why_it_matters = Column(Text, nullable=False, default="")
    completion_criteria = Column(Text, nullable=False, default="")
    expected_evidence_type = Column(Text, nullable=False, default="TERMINAL_LOG")
    status = Column(String, nullable=False, default="NOT_STARTED")
    order_index = Column(Integer, nullable=False)
    is_ai_proposed = Column(Boolean, nullable=False, default=False)
    is_archived = Column(Boolean, nullable=False, default=False)
    archived_at = Column(DateTime, nullable=True)
    archived_by = Column(String, nullable=True)
    justification = Column(Text)
    task = relationship("Task", back_populates="steps")
    evidence = relationship("Evidence", back_populates="step")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    source_task_id = Column(String, nullable=True)
    project = relationship("Project", back_populates="assets")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    step_id = Column(String, ForeignKey("task_steps.id"), nullable=True)
    # raw_content is retained only for pre-Day-2 migration compatibility.
    raw_content = Column(Text, nullable=True)
    evidence_type = Column(String, nullable=False, default="TERMINAL_LOG")
    file_path = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=False, default=0)
    sha256_hash = Column(String(64), nullable=False, default="")
    redacted_excerpt = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project = relationship("Project", back_populates="evidence")
    task = relationship("Task", back_populates="evidence")
    step = relationship("TaskStep", back_populates="evidence")

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, default="DRAFT")
    affected_asset = Column(String)
    description = Column(Text, nullable=False)
    reproduction_steps = Column(Text, nullable=False)
    remediation = Column(Text)
    evidence_id = Column(String, ForeignKey("evidence.id"))
    project = relationship("Project", back_populates="findings")

class WorkflowProposal(Base):
    __tablename__ = "workflow_proposals"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    phase_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    objective = Column(Text, nullable=False)
    priority = Column(String, default="MEDIUM")
    target_asset = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_task_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project = relationship("Project", back_populates="proposals")


class MentorMessage(Base):
    __tablename__ = "mentor_messages"
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    step_id = Column(String, ForeignKey("task_steps.id"), nullable=True)
    mode = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    ai_available = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    project = relationship("Project", back_populates="mentor_messages")
