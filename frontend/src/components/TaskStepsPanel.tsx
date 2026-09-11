import { useState } from 'react';
import { apiCall } from '../services/api';

const STATES = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CONFIRMED_NEGATIVE'];

export default function TaskStepsPanel({ projectId, task, locked, onChanged, onOpenMentor, onError }: {
  projectId: string;
  task: any;
  locked: boolean;
  onChanged: () => void;
  onOpenMentor: (step: any) => void;
  onError: (message: string) => void;
}) {
  const [title, setTitle] = useState('');
  const [creating, setCreating] = useState(false);
  const [openStepId, setOpenStepId] = useState<string | undefined>();
  const [raw, setRaw] = useState('');
  const [verifying, setVerifying] = useState(false);
  const [verdict, setVerdict] = useState<any>();
  const steps = task.steps ?? [];

  async function createStep() {
    if (!title.trim() || creating) return;
    setCreating(true);
    try {
      await apiCall(`/projects/${projectId}/tasks/${task.id}/steps`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), objective: '', why_it_matters: '', completion_criteria: '', expected_evidence_type: 'TERMINAL_LOG' }),
      });
      setTitle('');
      onChanged();
    } catch (err: any) {
      onError(err.message);
    } finally {
      setCreating(false);
    }
  }

  async function transition(step: any, status: string) {
    let justification: string | undefined;
    if (status === 'SKIPPED' || status === 'CONFIRMED_NEGATIVE') {
      justification = window.prompt('Justification (minimum 5 characters)', step.justification || '') || '';
      if (justification.trim().length < 5) return;
    }
    try {
      await apiCall(`/projects/${projectId}/tasks/${task.id}/steps/${step.id}/state`, {
        method: 'POST',
        body: JSON.stringify({ status, justification }),
      });
      onChanged();
    } catch (err: any) {
      onError(err.message);
    }
  }

  async function verifyStep(step: any) {
    if (!raw.trim() || verifying) return;
    setVerifying(true);
    setVerdict(undefined);
    try {
      const result = await apiCall<any>(`/projects/${projectId}/tasks/${task.id}/steps/${step.id}/verify`, {
        method: 'POST',
        body: JSON.stringify({ raw_content: raw }),
      });
      setVerdict(result);
      setRaw('');
      onChanged();
    } catch (err: any) {
      onError(err.message);
    } finally {
      setVerifying(false);
    }
  }

  function toggle(step: any) {
    setOpenStepId((current) => current === step.id ? undefined : step.id);
    setVerdict(undefined);
    setRaw('');
  }

  return <section className="task-steps">
    <div className="steps-heading"><h2>Task Steps</h2><small>{steps.length} active step{steps.length === 1 ? '' : 's'}</small></div>
    {steps.length === 0 && <p className="muted">No steps yet. Add a manual checkpoint below.</p>}
    {steps.map((step: any) => <div className="task-step-block" key={step.id}>
      <div className="task-step">
        <div><strong>{step.title}</strong><small>{step.status.replaceAll('_', ' ')}</small></div>
        <select value={step.status} onChange={(event) => transition(step, event.target.value)}>
          {STATES.map((state) => <option key={state} value={state}>{state.replaceAll('_', ' ')}</option>)}
        </select>
        <button onClick={() => toggle(step)}>{openStepId === step.id ? 'Close' : 'Open'}</button>
      </div>
      {openStepId === step.id && <div className="step-detail">
        {step.objective && <p>{step.objective}</p>}
        {step.completion_criteria && <p className="muted">Completion criteria: {step.completion_criteria}</p>}
        <textarea value={raw} onChange={(event) => setRaw(event.target.value)} placeholder={locked ? 'Paste human-collected output for this step...' : 'Lock scope to verify evidence'} disabled={!locked || verifying} />
        <div className="step-actions">
          <button onClick={() => verifyStep(step)} disabled={verifying || !locked || !raw.trim()}>{verifying ? 'Verifying...' : 'Verify Evidence'}</button>
          <button onClick={() => onOpenMentor(step)}>Ask Mentor</button>
        </div>
        {verdict && <div className="verdict"><strong>{verdict.verdict} · {verdict.confidence}</strong><p>{verdict.summary}</p>{verdict.grounded_quotations?.[0] && <blockquote>{verdict.grounded_quotations[0]}</blockquote>}<small>Saved as {verdict.evidence_id} · Step {verdict.step_status} · Task {verdict.task_status}</small></div>}
      </div>}
    </div>)}
    <div className="step-create"><input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="New step title" maxLength={300} /><button onClick={createStep} disabled={creating || !title.trim()}>{creating ? 'Adding...' : 'Add Step'}</button></div>
  </section>;
}
