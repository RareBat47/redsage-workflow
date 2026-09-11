import { useEffect, useState } from 'react';
import { apiCall } from '../services/api';

type MentorMode = 'teach' | 'guide' | 'verify' | 'summarize';

interface MentorMessage {
  role: 'user' | 'assistant';
  content: string;
  mode?: MentorMode;
  ai_available?: boolean | null;
}

const MODE_LABELS: Record<MentorMode, string> = {
  teach: 'Teach — explain the methodology',
  guide: 'Guide — safe tool options',
  verify: 'Verify — interpret evidence',
  summarize: 'Summarize — task status',
};

export default function MentorPanel({ projectId, task, step, targetHost, onError }: {
  projectId: string;
  task: any;
  step?: any;
  targetHost: string;
  onError: (message: string) => void;
}) {
  const [mode, setMode] = useState<MentorMode>('teach');
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const scopeKey = `${projectId}:${task.id}:${step?.id ?? 'task'}`;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    apiCall<MentorMessage[]>(`/projects/${projectId}/tasks/${task.id}/mentor/history${step ? `?step_id=${encodeURIComponent(step.id)}` : ''}`)
      .then((history) => { if (!cancelled) setMessages(history); })
      .catch((err: any) => { if (!cancelled) onError(err.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [scopeKey]);

  async function send() {
    const question = input.trim();
    if (!question || busy) return;
    setInput('');
    setBusy(true);
    try {
      const result = await apiCall<any>(`/projects/${projectId}/tasks/${task.id}/mentor`, {
        method: 'POST',
        body: JSON.stringify({ mode, user_message: question, target_host: targetHost || undefined, step_id: step?.id }),
      });
      const history = await apiCall<MentorMessage[]>(`/projects/${projectId}/tasks/${task.id}/mentor/history${step ? `?step_id=${encodeURIComponent(step.id)}` : ''}`);
      setMessages(history);
      if (!history.length) setMessages([{ role: 'user', content: question }, { role: 'assistant', content: result.reply, mode: result.mode, ai_available: result.ai_available }]);
    } catch (err: any) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return <div className="mentor-panel">
    <header className="mentor-head"><b>AI MENTOR</b><small>{step ? `${task.title} / ${step.title}` : task.title}</small></header>
    <p className="mentor-hint">Methodology guidance only. RedSage never executes anything and the mentor will not provide exploit material.</p>
    <select value={mode} disabled={busy} onChange={(event) => setMode(event.target.value as MentorMode)}>
      {(Object.keys(MODE_LABELS) as MentorMode[]).map((item) => <option key={item} value={item}>{MODE_LABELS[item]}</option>)}
    </select>
    <div className="mentor-messages">
      {loading && <p className="mentor-empty">Loading saved conversation...</p>}
      {!loading && messages.length === 0 && <p className="mentor-empty">Ask a question about this task, its methodology, or how to interpret captured evidence.</p>}
      {messages.map((message, index) => message.role === 'user'
        ? <div className="mentor-msg analyst" key={`${message.role}-${index}`}>{message.content}</div>
        : <div className="mentor-msg mentor" key={`${message.role}-${index}`}><small>{message.mode} {message.ai_available === false ? '(AI unavailable — static checklist)' : ''}</small>{message.content}</div>)}
      {busy && <div className="mentor-msg mentor thinking"><small>thinking...</small>Mentor is reviewing the task context. This can take 5–15 seconds.</div>}
    </div>
    <div className="mentor-input">
      <textarea value={input} disabled={busy} placeholder="Ask about methodology, tool options, or evidence interpretation..." onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }} />
      <button disabled={busy || !input.trim()} onClick={send}>{busy ? 'Sending...' : 'Send'}</button>
    </div>
  </div>;
}
