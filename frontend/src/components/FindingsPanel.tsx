import { useState } from 'react';
import { apiCall } from '../services/api';
import type { EvidenceItem } from '../types';

interface Finding {
  id: string;
  title: string;
  severity: string;
  status: string;
  affected_asset: string | null;
  description: string;
  reproduction_steps: string;
  remediation: string | null;
  evidence_id: string | null;
}

const SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export default function FindingsPanel({ projectId, findings, evidence, onChanged, onError }: {
  projectId: string;
  findings: Finding[];
  evidence: EvidenceItem[];
  onChanged: () => void;
  onError: (message: string) => void;
}) {
  const [confirmingId, setConfirmingId] = useState<string | null>(null);
  const [form, setForm] = useState({ title: '', severity: 'HIGH', description: '', reproduction_steps: '', remediation: '', affected_asset: '', evidence_id: '' });
  const [formError, setFormError] = useState('');
  const [busy, setBusy] = useState(false);

  const drafts = findings.filter((finding) => finding.status !== 'CONFIRMED');
  const confirmed = findings.filter((finding) => finding.status === 'CONFIRMED');

  async function createDraft() {
    const title = window.prompt('Draft finding title');
    if (!title) return;
    try {
      await apiCall(`/projects/${projectId}/findings`, { method: 'POST', body: JSON.stringify({ title, severity: 'MEDIUM' }) });
      onChanged();
    } catch (err: any) { onError(err.message); }
  }

  function openConfirm(finding: Finding) {
    setConfirmingId(finding.id);
    setFormError('');
    setForm({
      title: finding.title || '',
      severity: SEVERITIES.includes(finding.severity) ? finding.severity : 'HIGH',
      description: finding.description || '',
      reproduction_steps: finding.reproduction_steps || '',
      remediation: finding.remediation || '',
      affected_asset: finding.affected_asset || '',
      evidence_id: finding.evidence_id || (evidence[0]?.evidence_id ?? ''),
    });
  }

  async function submitConfirm() {
    if (!confirmingId || busy) return;
    setBusy(true); setFormError('');
    try {
      await apiCall(`/projects/${projectId}/findings/${confirmingId}/confirm`, {
        method: 'POST',
        body: JSON.stringify({
          evidence_id: form.evidence_id,
          title: form.title,
          severity: form.severity,
          description: form.description,
          reproduction_steps: form.reproduction_steps,
          remediation: form.remediation || undefined,
          affected_asset: form.affected_asset || undefined,
        }),
      });
      setConfirmingId(null);
      onChanged();
    } catch (err: any) {
      setFormError(err.message || 'Confirm failed');
    } finally { setBusy(false); }
  }

  return <section>
    <h2>Findings</h2>
    <button onClick={createDraft}>+ Log Draft</button>
    <p className="finding-hint">Drafts require no evidence. Confirming requires linked evidence, description, and reproduction steps. Only confirmed findings enter the report.</p>

    <h3>Drafts ({drafts.length})</h3>
    {drafts.length === 0 && <p className="finding-empty">No draft findings.</p>}
    {drafts.map((finding) => <div className="finding draft" key={finding.id}>
      <span>{finding.title} <b>{finding.severity}</b></span>
      {confirmingId === finding.id ? null : <button onClick={() => openConfirm(finding)}>Confirm</button>}
      {confirmingId === finding.id && <div className="confirm-form">
        <label>CONFIRM FINDING</label>
        <select value={form.evidence_id} onChange={(event) => setForm({ ...form, evidence_id: event.target.value })}>
          <option value="">Select evidence...</option>
          {evidence.map((item) => <option key={item.evidence_id} value={item.evidence_id}>{item.evidence_id} — {item.task_title || item.task_id}</option>)}
        </select>
        <input placeholder="Title" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
        <select value={form.severity} onChange={(event) => setForm({ ...form, severity: event.target.value })}>
          {SEVERITIES.map((severity) => <option key={severity} value={severity}>{severity}</option>)}
        </select>
        <textarea className="small" placeholder="Description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
        <textarea className="small" placeholder="Reproduction steps" value={form.reproduction_steps} onChange={(event) => setForm({ ...form, reproduction_steps: event.target.value })} />
        <textarea className="small" placeholder="Remediation (optional)" value={form.remediation} onChange={(event) => setForm({ ...form, remediation: event.target.value })} />
        <input placeholder="Affected asset (optional)" value={form.affected_asset} onChange={(event) => setForm({ ...form, affected_asset: event.target.value })} />
        {formError && <div className="error inline">{formError}</div>}
        <div className="confirm-actions">
          <button disabled={busy} onClick={submitConfirm}>{busy ? 'Confirming...' : 'Confirm Finding'}</button>
          <button disabled={busy} onClick={() => { setConfirmingId(null); setFormError(''); }}>Cancel</button>
        </div>
      </div>}
    </div>)}

    <h3>Confirmed ({confirmed.length})</h3>
    {confirmed.length === 0 && <p className="finding-empty">No confirmed findings.</p>}
    {confirmed.map((finding) => <div className="finding confirmed" key={finding.id}>
      <span>{finding.title} <b>{finding.severity}</b></span>
      <small>Evidence: {finding.evidence_id || 'MISSING'}</small>
    </div>)}
  </section>;
}
