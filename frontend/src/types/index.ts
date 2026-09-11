export interface EvidenceItem {
  evidence_id: string;
  task_id: string;
  task_title: string | null;
  step_id?: string | null;
  step_title?: string | null;
  created_at: string;
  file_path: string | null;
  file_size_bytes: number;
  sha256_hash: string;
  redacted_excerpt: string;
}
