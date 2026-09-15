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

export type TaskStatus =
  | 'NOT_STARTED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'SKIPPED'
  | 'CONFIRMED_NEGATIVE';

export type VerificationVerdict = 'PASS' | 'FAIL' | 'AMBIGUOUS' | 'CONFIRMED_NEGATIVE';

export type VerificationConfidence = 'HIGH' | 'MEDIUM' | 'LOW';

export type ExtractedAssetType = 'HOST' | 'PORT' | 'ENDPOINT' | 'FILE';

export interface ExtractedAsset {
  type: ExtractedAssetType;
  value: string;
}

export interface TaskVerificationResponse {
  verdict: VerificationVerdict;
  confidence: VerificationConfidence;
  summary: string;
  grounded_quotations: string[];
  extracted_assets: ExtractedAsset[];
  evidence_id: string;
  task_status: TaskStatus;
}

export interface StepVerificationResponse extends TaskVerificationResponse {
  step_status: TaskStatus;
}

export interface TaskStepSummary {
  id: string;
  title: string;
  status: TaskStatus;
  order_index: number;
  is_archived: boolean;
  objective?: string;
  completion_criteria?: string;
  justification?: string | null;
}
