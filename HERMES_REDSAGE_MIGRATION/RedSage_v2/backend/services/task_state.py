from sqlalchemy.orm import Session

from backend.models.schema import Task, TaskStep
from backend.services.audit_service import record_event


ALLOWED_TASK_STATES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    "SKIPPED",
    "CONFIRMED_NEGATIVE",
}
TERMINAL_TASK_STATES = {"COMPLETED", "SKIPPED", "CONFIRMED_NEGATIVE"}


class StateTransitionError(ValueError):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


def validate_state_transition(status: str, justification: str | None) -> None:
    if status not in ALLOWED_TASK_STATES:
        raise StateTransitionError("Invalid task status", 422)
    if status in {"SKIPPED", "CONFIRMED_NEGATIVE"} and len((justification or "").strip()) < 5:
        raise StateTransitionError("Justification required", 400)


def active_steps(task: Task, db: Session) -> list[TaskStep]:
    return (
        db.query(TaskStep)
        .filter(TaskStep.task_id == task.id, TaskStep.is_archived.is_(False))
        .order_by(TaskStep.order_index, TaskStep.id)
        .all()
    )


def rollup_task_from_steps(task: Task, project_id: str, db: Session) -> bool:
    steps = active_steps(task, db)
    if not steps:
        return False
    if all(step.status in TERMINAL_TASK_STATES for step in steps):
        previous_status = task.status
        if previous_status != "COMPLETED":
            task.status = "COMPLETED"
            record_event(
                db,
                project_id,
                "TASK_STATE_CHANGED",
                "task",
                task.id,
                {"from": previous_status, "to": "COMPLETED", "justification": "All active steps reached a terminal state."},
            )
        return True
    # Recalculate downward: active steps are no longer all terminal (for example
    # an operator reverted a Step). A task must not remain COMPLETED while any of
    # its active steps is still open.
    if task.status == "COMPLETED":
        task.status = "IN_PROGRESS"
        record_event(
            db,
            project_id,
            "TASK_STATE_CHANGED",
            "task",
            task.id,
            {"from": "COMPLETED", "to": "IN_PROGRESS", "justification": "Active steps are no longer all terminal; task completion recalculated."},
        )
    return False
