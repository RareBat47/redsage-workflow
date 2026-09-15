import { useState } from 'react';
import { apiCall } from '../services/api';

export default function ProjectBriefPanel({ project, onClose, onSaved, onError }: {
  project: any;
  onClose: () => void;
  onSaved: (brief: string) => void;
  onError: (message: string) => void;
}) {
  const [brief, setBrief] = useState(project.brief ?? '');
  const [saving, setSaving] = useState(false);

  async function save() {
    if (saving) return;
    setSaving(true);
    try {
      const result = await apiCall<{ brief: string }>(`/projects/${project.id}/brief`, {
        method: 'PUT',
        body: JSON.stringify({ text: brief }),
      });
      onSaved(result.brief);
      onClose();
    } catch (err: any) {
      onError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return <div className="modal-backdrop">
    <div className="modal form-modal project-brief-panel">
      <div className="modal-head"><strong>PROJECT BRIEF</strong><button onClick={onClose}>Close</button></div>
      <p>Describe the engagement, authorized scope, constraints, timebox, and desired assessment focus. This brief will guide future workflow generation.</p>
      <label htmlFor="project-brief">Describe your problem</label>
      <textarea id="project-brief" value={brief} maxLength={20000} onChange={(event) => setBrief(event.target.value)} placeholder="Describe the authorized engagement and what you need to learn..." />
      <small className="brief-counter">{brief.length}/20000</small>
      <button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save Brief'}</button>
    </div>
  </div>;
}
