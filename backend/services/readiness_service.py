from backend.services.task_state import TERMINAL_TASK_STATES


def calculate_phase_coverage(phases, tasks) -> dict[str, int]:
    """Return active phase coverage using the same Task denominator as Readiness."""
    active_tasks = [task for task in tasks if not getattr(task, "is_archived", False)]
    return {
        phase.name: round(
            sum(task.status in TERMINAL_TASK_STATES for task in active_tasks if task.phase_id == phase.id)
            * 100
            / len([task for task in active_tasks if task.phase_id == phase.id])
        ) if [task for task in active_tasks if task.phase_id == phase.id] else 0
        for phase in phases
        if not getattr(phase, "is_archived", False)
    }
