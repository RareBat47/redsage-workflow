import json
import uuid
from sqlalchemy.orm import Session
from backend.models.schema import Phase, Task

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
