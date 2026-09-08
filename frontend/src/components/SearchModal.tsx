import { useEffect, useState } from 'react';
import { apiCall } from '../services/api';

interface Props { projectId: string; onClose: () => void; onNavigate: (view: 'roadmap' | 'evidence' | 'assets') => void; }

export default function SearchModal({ projectId, onClose, onNavigate }: Props) {
  const [query, setQuery] = useState(''); const [results, setResults] = useState<any>({ findings: [], evidence: [], assets: [] });
  useEffect(() => { if (query.trim()) apiCall(`/projects/${projectId}/search?q=${encodeURIComponent(query)}`).then(setResults).catch(() => setResults({ findings: [], evidence: [], assets: [] })); }, [projectId, query]);
  return <div className="modal-backdrop"><div className="modal search-modal"><div className="modal-head"><strong>SEARCH PROJECT</strong><button onClick={onClose}>Close</button></div><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search findings, evidence, and assets" />{(['findings', 'evidence', 'assets'] as const).map((group) => <section key={group}><h3>{group}</h3>{results[group].map((result: any) => <button className="search-result" key={result.id} onClick={() => { onNavigate(result.target_view); onClose(); }}>{result.title}<small>{result.snippet}</small></button>)}</section>)}</div></div>;
}
