import { useState } from 'react';
import type { EvidenceItem } from '../types';
import EvidenceModal from '../components/EvidenceModal';

interface Props { evidence: EvidenceItem[]; projectId: string; }

export default function EvidenceLibrary({ evidence, projectId }: Props) {
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<EvidenceItem | null>(null);
  const filtered = evidence.filter((item) => `${item.evidence_id} ${item.task_title || ''} ${item.redacted_excerpt}`.toLowerCase().includes(search.toLowerCase()));
  return <section className="library"><div className="library-head"><div><label>EVIDENCE LIBRARY</label><h1>{evidence.length} Artifacts</h1></div><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search evidence..." /></div>
    <div className="evidence-list">{filtered.map((item) => <article className="evidence-card" key={item.evidence_id}><div className="evidence-meta"><mark>{item.evidence_id}</mark><strong>{item.task_title || item.task_id}</strong><span>{item.file_size_bytes} B</span><time>{new Date(item.created_at).toLocaleString()}</time></div><code>{item.sha256_hash.slice(0, 18)}... <button onClick={() => navigator.clipboard.writeText(item.sha256_hash)}>Copy SHA</button></code><details><summary>Redacted excerpt</summary><pre>{item.redacted_excerpt}</pre></details><button onClick={() => setSelected(item)}>View Full Artifact</button></article>)}</div>
     {selected && <EvidenceModal item={selected} projectId={projectId} onClose={() => setSelected(null)} />}
  </section>;
}
