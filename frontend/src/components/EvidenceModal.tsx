import { useEffect, useState } from 'react';
import type { EvidenceItem } from '../types';

interface Props {
  item: EvidenceItem;
  projectId: string;
  onClose: () => void;
}

export default function EvidenceModal({ item, projectId, onClose }: Props) {
  const [content, setContent] = useState('Loading artifact...');
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/v1/projects/${projectId}/evidence/${item.evidence_id}/content`)
      .then((response) => response.json())
      .then((body) => setContent(body.content || body.detail || 'Artifact unavailable'))
      .catch(() => setContent('Artifact unavailable'));
  }, [item, projectId]);
  return <div className="modal-backdrop" onClick={onClose}>
    <div className="modal" onClick={(event) => event.stopPropagation()}>
      <div className="modal-head"><strong>{item.evidence_id}</strong><button onClick={onClose}>Close</button></div>
      <pre className="full-artifact">{content}</pre>
      <button onClick={() => navigator.clipboard.writeText(content)}>Copy Content</button>
    </div>
  </div>;
}
