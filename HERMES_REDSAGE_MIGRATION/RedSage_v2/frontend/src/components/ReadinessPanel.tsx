import { useEffect, useState } from 'react';
import { apiCall } from '../services/api';

export default function ReadinessPanel({ projectId }: { projectId: string }) {
  const [data, setData] = useState<any>();
  useEffect(() => { apiCall(`/projects/${projectId}/report/readiness`).then(setData).catch(() => setData(undefined)); }, [projectId]);
  if (!data) return <aside className="readiness"><strong>REPORT READINESS</strong><p>Loading...</p></aside>;
  return <aside className="readiness"><strong>REPORT READINESS</strong><h2>{data.score}%</h2><p className={data.ready_for_export ? 'ready' : 'critical'}>{data.ready_for_export ? 'Ready for export' : 'Critical issues require attention'}</p>{data.issues.map((issue: any, index: number) => <div className={`issue ${issue.severity.toLowerCase()}`} key={`${issue.entity_id}-${index}`}><b>{issue.severity}</b> {issue.message}</div>)}<h3>Methodology coverage</h3>{Object.entries(data.coverage).map(([name, percentage]) => <p key={name}>{name}: <b>{percentage as number}%</b></p>)}</aside>;
}
