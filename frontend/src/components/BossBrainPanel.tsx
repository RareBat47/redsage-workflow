import { useEffect, useState } from 'react';
import { apiCall } from '../services/api';

type Message = { role: 'user' | 'assistant'; content: string; mode?: string; ai_available?: boolean | null };

export default function BossBrainPanel({ projectId, tasks, onError }: { projectId: string; tasks: any[]; onError: (message: string) => void }) {
  const [digest, setDigest] = useState<any>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const [nextDigest, history] = await Promise.all([
        apiCall<any>(`/projects/${projectId}/workflow/digest`),
        apiCall<Message[]>(`/projects/${projectId}/mentor/boss/history`),
      ]);
      setDigest(nextDigest);
      setMessages(history);
    } catch (err: any) { onError(err.message); }
  }

  useEffect(() => { load(); }, [projectId]);

  async function ask() {
    const question = input.trim();
    if (!question || busy) return;
    setInput(''); setBusy(true);
    try {
      await apiCall(`/projects/${projectId}/mentor/boss`, { method: 'POST', body: JSON.stringify({ mode: 'summarize', user_message: question }) });
      await load();
    } catch (err: any) { onError(err.message); }
    finally { setBusy(false); }
  }

  return <section className="boss-brain">
    <div className="boss-tree"><label>BOSS BRAIN / READ-ONLY WORKFLOW</label>{tasks.map((phase: any) => <section key={phase.id}><strong>{phase.name}</strong>{phase.tasks.map((task: any) => <div className="boss-task" key={task.id}>{task.status === 'COMPLETED' ? '✓' : '○'} {task.title}{task.steps?.length ? <small>{task.steps.length} active steps</small> : null}</div>)}</section>)}</div>
    <div className="boss-chat"><div className="boss-digest"><label>MEASURED PROJECT DIGEST</label>{digest?.phases?.map((phase: any) => <div className="digest-row" key={phase.name}><strong>{phase.name}</strong><span>{phase.coverage}% coverage · {phase.asset_count} assets · {phase.confirmed_finding_count} confirmed findings</span></div>)}<small>{digest?.evidence_count ?? 0} evidence records · {digest?.confirmed_finding_count ?? 0} confirmed findings</small></div><div className="boss-messages">{messages.length === 0 && <p className="muted">Ask about status, prioritization, or report readiness. Answers use measured project data only.</p>}{messages.map((message, index) => <div className={`boss-message ${message.role}`} key={`${message.role}-${index}`}>{message.content}</div>)}{busy && <div className="boss-message assistant">thinking...</div>}</div><div className="boss-input"><textarea value={input} disabled={busy} placeholder="What is my current status?" onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); ask(); } }} /><button disabled={busy || !input.trim()} onClick={ask}>{busy ? 'Thinking...' : 'Ask Boss Brain'}</button></div></div>
  </section>;
}
