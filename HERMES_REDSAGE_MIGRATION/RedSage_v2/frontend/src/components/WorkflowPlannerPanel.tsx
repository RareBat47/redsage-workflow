import { useState } from 'react';
import { apiCall } from '../services/api';

type PlannerResult = {
  status: 'NEEDS_CLARIFICATION' | 'READY';
  questions: { id: string; question: string }[];
  draft: any;
  ai_available: boolean;
};

export default function WorkflowPlannerPanel({ project, onClose, onApplied, onError }: {
  project: any;
  onClose: () => void;
  onApplied: () => void;
  onError: (message: string) => void;
}) {
  const [result, setResult] = useState<PlannerResult | undefined>();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  async function generate() {
    if (busy) return;
    setBusy(true);
    try {
      setResult(await apiCall<PlannerResult>(`/projects/${project.id}/workflow/generate`, { method: 'POST' }));
    } catch (err: any) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function saveAnswersAndGenerate() {
    const additions = Object.entries(answers).filter(([, value]) => value.trim()).map(([id, value]) => `${id}: ${value.trim()}`).join('\n');
    if (!additions) return;
    setBusy(true);
    try {
      await apiCall(`/projects/${project.id}/brief`, { method: 'PUT', body: JSON.stringify({ text: `${project.brief || ''}\n${additions}`.trim() }) });
      setResult(await apiCall<PlannerResult>(`/projects/${project.id}/workflow/generate`, { method: 'POST' }));
    } catch (err: any) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function apply(mode: 'replace' | 'merge') {
    if (!result?.draft || busy) return;
    setBusy(true);
    try {
      await apiCall(`/projects/${project.id}/workflow/apply`, { method: 'POST', body: JSON.stringify({ mode, draft: result.draft }) });
      onApplied();
      onClose();
    } catch (err: any) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return <div className="modal-backdrop">
    <div className="modal planner-panel">
      <div className="modal-head"><strong>WORKFLOW PLANNER</strong><button onClick={onClose}>Close</button></div>
      <p>Generate a proposed seven-phase workflow from the saved Project Brief. Nothing changes until you explicitly Apply it.</p>
      {!result && <button onClick={generate} disabled={busy}>{busy ? 'Planning...' : 'Generate Workflow'}</button>}
      {result?.status === 'NEEDS_CLARIFICATION' && <section className="planner-questions">
        <h2>Clarification Needed</h2>
        <p>Answer the missing engagement questions before the Planner can produce a draft.</p>
        {result.questions.map((question) => <label key={question.id}>{question.question}<textarea value={answers[question.id] || ''} onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))} /></label>)}
        <button onClick={saveAnswersAndGenerate} disabled={busy}>{busy ? 'Saving...' : 'Save Answers and Generate'}</button>
      </section>}
      {result?.status === 'READY' && result.draft && <section className="planner-preview">
        <div className="planner-status">{result.ai_available ? 'AI draft ready for review.' : 'Offline baseline draft ready for review.'}</div>
        {result.draft.phases.map((phase: any) => <details key={phase.name} open><summary>{phase.name} ({phase.tasks.length} tasks)</summary><div className="planner-phase">{phase.tasks.map((task: any) => <div className="planner-task" key={task.title}><strong>{task.title}</strong><p>{task.objective}</p>{task.steps.map((step: any) => <small key={step.title}>Step: {step.title} · {step.expected_evidence_type}</small>)}</div>)}</div></details>)}
        <div className="planner-actions"><button onClick={() => apply('replace')} disabled={busy}>Apply Replace (Archive Old)</button><button onClick={() => apply('merge')} disabled={busy}>Apply Merge</button><button onClick={() => setResult(undefined)} disabled={busy}>Discard Draft</button></div>
      </section>}
    </div>
  </div>;
}
