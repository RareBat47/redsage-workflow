import json
import uuid
import datetime
from sqlalchemy.orm import Session
from backend.models.schema import Phase, Task, TaskStep
from backend.services.planner_service import WorkflowDraft

def seed_project_tasks(project_id: str, db: Session, methodology_path: str = "data/methodologies/baseline_methodology.json"):
    with open(methodology_path, encoding="utf-8") as file:
        data = json.load(file)
    for phase_data in data:
        phase = Phase(id=str(uuid.uuid4()), project_id=project_id, name=phase_data["phase_name"], order_index=phase_data["order_index"])
        db.add(phase)
        db.flush()
        for task_data in phase_data["tasks"]:
            db.add(Task(id=str(uuid.uuid4()), phase_id=phase.id, project_id=project_id, title=task_data["title"], objective=task_data["objective"], command_template=task_data["command_template"], priority=task_data["priority"], order_index=task_data["order_index"], status="NOT_STARTED", is_ai_proposed=False))
    db.commit()


def insert_workflow_draft(project_id: str, draft: WorkflowDraft, db: Session, merge: bool = False) -> None:
    """Insert a validated draft under active canonical phases."""
    phases = {phase.name: phase for phase in db.query(Phase).filter(Phase.project_id == project_id, Phase.is_archived.is_(False)).all()}
    for phase_draft in draft.phases:
        phase = phases.get(phase_draft.name)
        if phase is None:
            phase = Phase(id=str(uuid.uuid4()), project_id=project_id, name=phase_draft.name, order_index=phase_draft.order_index, is_archived=False)
            db.add(phase)
            db.flush()
            phases[phase.name] = phase
        active_tasks = [task for task in phase.tasks if not task.is_archived]
        next_order = max((task.order_index for task in active_tasks), default=0) + 1
        existing_titles = {task.title for task in active_tasks}
        for task_draft in phase_draft.tasks:
            if merge and task_draft.title in existing_titles:
                continue
            task = Task(
                id=str(uuid.uuid4()),
                phase_id=phase.id,
                project_id=project_id,
                title=task_draft.title,
                objective=task_draft.objective,
                command_template=task_draft.command_template,
                priority=task_draft.priority,
                order_index=next_order,
                status="NOT_STARTED",
                is_ai_proposed=task_draft.is_ai_proposed,
                is_archived=False,
            )
            next_order += 1
            db.add(task)
            db.flush()
            existing_titles.add(task.title)
            for step_index, step_draft in enumerate(task_draft.steps, start=1):
                db.add(TaskStep(
                    id=str(uuid.uuid4()),
                    task_id=task.id,
                    title=step_draft.title,
                    objective=step_draft.objective,
                    why_it_matters=step_draft.why_it_matters,
                    completion_criteria=step_draft.completion_criteria,
                    expected_evidence_type=step_draft.expected_evidence_type,
                    order_index=step_index,
                    is_ai_proposed=step_draft.is_ai_proposed,
                    is_archived=False,
                    status="NOT_STARTED",
                ))


def archive_active_workflow(project_id: str, db: Session) -> None:
    now = datetime.datetime.utcnow()
    for task in db.query(Task).filter(Task.project_id == project_id, Task.is_archived.is_(False)).all():
        task.is_archived = True
        task.archived_at = now
        task.archived_by = "planner_replace"
        for step in task.steps:
            if not step.is_archived:
                step.is_archived = True
                step.archived_at = now
                step.archived_by = "planner_replace"
    return None
