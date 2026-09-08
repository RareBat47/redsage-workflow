import type { EvidenceItem } from '../types';

export const API = 'http://127.0.0.1:8000/api/v1';

export async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw Error(body.detail || 'Request failed');
  }
  return response.json();
}

export function getProjectEvidence(projectId: string) {
  return apiCall<EvidenceItem[]>(`/projects/${projectId}/evidence`);
}

export function getEvidenceContent(projectId: string, evidenceId: string) {
  return apiCall<{ content: string }>(`/projects/${projectId}/evidence/${evidenceId}/content`);
}
