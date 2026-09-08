import { useState } from 'react';
import { apiCall } from '../services/api';

type MentorMode = 'teach' | 'guide' | 'verify' | 'summarize';

interface MentorMessage {
  role: 'analyst' | 'mentor';
  text: string;
  mode?: MentorMode;
  aiAvailable?: boolean;
}

const MODE_LABELS: Record<MentorMode, string> = {
  teach: 'Teach — explain the methodology',
  guide: 'Guide — safe tool options',
  verify: 'Verify — interpret evidence',
  summarize: 'Summarize — task status',
};

const conversations = new Map<string, MentorMessage[]>();

export default function MentorPanel({ projectId, task, targetHost, onError }: {
  projectId: string;
  task: any;
  targetHost: string;
  onError: (message: string) => void;
}) {
  const [mode, setMode] = useState<MentorMode>('teach');
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [, setTick] = useState(0);
  const key = `${projectId}:${task.id}`;
  const messages = conversations.get(key) ?? [];

  function push(message: MentorMessage) {
    conversations.set(key, [...(conversations.get(key) ?? []), message]);
    setTick((tick) => tick + 1);
  }

  async function send() {
    const question = input.trim();
    if (!question || busy) return;
    push({ role: 'analyst', text: question });
    setInput('');
    setBusy(true);
    try {
      const result = await apiCall<any>(`/projects/${projectId}/tasks/${task.id}/mentor`, {
        method: 'POST',
        body: JSON.stringify({ mode, user_message: question, target_host: targetHost || undefined }),
      });
      push({ role: 'mentor', text: result.reply, mode: result.mode, aiAvailable: result.ai_available });
    } catch (err: any) {
      onError(err.message);
      push({ role: 'mentor', text: `Mentor request failed: ${err.message}`, aiAvailable: false });
    } finally {
      setBusy(false);
    }
  }

  return <div className="mentor-panel">
    <header className="mentor-head"><b>AI MENTOR</b><small>{task.title}</small></header>
    <p className="mentor-hint">Methodology guidance only. RedSage never executes anything and the mentor will not provide exploit material.</p>
    <select value={mode} disabled={busy} onChange={(event) => setMode(event.target.value as MentorMode)}>
      {(Object.keys(MODE_LABELS) as MentorMode[]).map((item) => <option key={item} value={item}>{MODE_LABELS[item]}</option>)}
    </select>
    <div className="mentor-messages">
      {messages.length === 0 && <p className="mentor-empty">Ask a question about this task, its methodology, or how to interpret captured evidence.</p>}
      {messages.map((message, index) => message.role === 'analyst'
        ? <div className="mentor-msg analyst" key={index}>{message.text}</div>
        : <div className="mentor-msg mentor" key={index}>
            <small>{message.mode} {message.aiAvailable === false ? '(AI unavailable — static checklist)' : ''}</small>
            {message.text}
          </div>)}
      {busy && <div className="mentor-msg mentor thinking"><small>thinking...</small>Mentor is reviewing the task context. This can take 5–15 seconds.</div>}
    </div>
    <div className="mentor-input">
      <textarea
        value={input}
        disabled={busy}
        placeholder="Ask about methodology, tool options, or evidence interpretation..."
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); send(); } }}
      />
      <button disabled={busy || !input.trim()} onClick={send}>{busy ? 'Sending...' : 'Send'}</button>
    </div>
  </div>;
}
