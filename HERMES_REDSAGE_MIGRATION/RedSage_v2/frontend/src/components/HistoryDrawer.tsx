import { useEffect, useState } from 'react';
import { apiCall } from '../services/api';

interface Props { projectId: string; onClose: () => void; onChanged: () => void; }

export default function HistoryDrawer({ projectId, onClose, onChanged }: Props) {
  const [events, setEvents] = useState<any[]>([]);
  useEffect(() => { apiCall<any[]>(`/projects/${projectId}/audit-log`).then(setEvents).catch(() => setEvents([])); }, [projectId]);
  async function undo(event: any) {
    if (event.event_type !== 'PROPOSAL_APPROVED' || !event.entity_id) return;
    try { await apiCall(`/projects/${projectId}/proposals/${event.entity_id}/undo`, { method: 'POST' }); onChanged(); setEvents(await apiCall<any[]>(`/projects/${projectId}/audit-log`)); } catch { /* ineligible entries remain visible */ }
  }
  return <div className="modal-backdrop"><div className="modal drawer"><div className="modal-head"><strong>PROJECT AUDIT & HISTORY</strong><button onClick={onClose}>Close</button></div>{events.map((event) => <div className="history-event" key={event.id}><b>{event.event_type}</b><time>{new Date(event.created_at).toLocaleString()}</time><pre>{JSON.stringify(event.details, null, 2)}</pre>{event.can_undo && <button onClick={() => undo(event)}>Undo Addition</button>}</div>)}</div></div>;
}
