import json
import uuid
from sqlalchemy.orm import Session
from backend.models.schema import AuditEvent

def record_event(db: Session, project_id: str, event_type: str, entity_type: str | None = None, entity_id: str | None = None, details: dict | None = None):
    event = AuditEvent(id=str(uuid.uuid4()), project_id=project_id, event_type=event_type, entity_type=entity_type, entity_id=entity_id, details=json.dumps(details or {}))
    db.add(event)
    return event
