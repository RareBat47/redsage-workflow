import { useEffect, useState } from 'react';
import { apiCall } from '../services/api';

export default function AssetsView({ projectId, onChanged }: { projectId: string; onChanged: () => void }) {
  const [assets, setAssets] = useState<any[]>([]); const [query, setQuery] = useState(''); const [message, setMessage] = useState('');
  const load = () => apiCall<any[]>(`/projects/${projectId}/assets`).then(setAssets).catch(() => setAssets([]));
  useEffect(load, [projectId]);
  const filtered = assets.filter((asset) => `${asset.type} ${asset.value}`.toLowerCase().includes(query.toLowerCase()));
  async function suggest(asset: any) { try { const result = await apiCall<any>(`/projects/${projectId}/assets/${asset.id}/suggest-tasks`, { method: 'POST' }); setMessage(`${result.created_count} governed proposal(s) added to the queue.`); onChanged(); } catch (err: any) { setMessage(err.message); } }
  return <section className="library"><div className="library-head"><div><label>DISCOVERED TARGET ASSETS</label><h1>{assets.length} Assets</h1></div><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search assets..." /></div>{message && <p className="saved">{message}</p>}<div className="asset-table"><div className="asset-row asset-header"><b>Type</b><b>Asset Identifier</b><b>Source Task</b><b>Action</b></div>{filtered.map((asset) => <div className="asset-row" key={asset.id}><span>{asset.type}</span><strong>{asset.value}</strong><span>{asset.source_task || 'Evidence-derived'}</span><button onClick={() => suggest(asset)}>Suggest Tasks</button></div>)}</div></section>;
}
