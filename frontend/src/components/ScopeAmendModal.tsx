import { useState } from 'react';
import { apiCall } from '../services/api';

interface Props { projectId: string; onClose: () => void; onSaved: () => void; }

export default function ScopeAmendModal({ projectId, onClose, onSaved }: Props) {
  const [targets, setTargets] = useState('');
  const [authorizedBy, setAuthorizedBy] = useState('');
  const [rationale, setRationale] = useState('');
  const [error, setError] = useState('');
  async function submit() {
    try {
      await apiCall(`/projects/${projectId}/scope/amend`, { method: 'POST', body: JSON.stringify({ additional_targets: targets.split('\n').map((item) => item.trim()).filter(Boolean), authorized_by: authorizedBy, rationale }) });
      onSaved(); onClose();
    } catch (err: any) { setError(err.message); }
  }
  return <div className="modal-backdrop"><div className="modal form-modal"><div className="modal-head"><strong>AMEND AUTHORIZED SCOPE</strong><button onClick={onClose}>Close</button></div><p>Amendments are permanently recorded in the audit trail and report.</p><label>Additional target(s), one per line</label><textarea value={targets} onChange={(event) => setTargets(event.target.value)} /><label>Authorizing entity / contact</label><input value={authorizedBy} onChange={(event) => setAuthorizedBy(event.target.value)} /><label>Justification, minimum 10 characters</label><textarea value={rationale} onChange={(event) => setRationale(event.target.value)} />{error && <div className="error">{error}</div>}<button onClick={submit} disabled={!targets || !authorizedBy || rationale.trim().length < 10}>Confirm Amendment</button></div></div>;
}
