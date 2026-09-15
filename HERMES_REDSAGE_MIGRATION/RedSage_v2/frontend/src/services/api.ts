import type { EvidenceItem } from '../types';

// Vite dev proxies nothing by default — hit the engine directly.
// Production SPA is served by FastAPI, so same-origin `/api/v1` is preferred.
// Override either mode with VITE_API_BASE (no trailing slash).
const metaEnv = (import.meta as any).env || {};
export const API = (
  typeof metaEnv.VITE_API_BASE === 'string' && metaEnv.VITE_API_BASE
    ? String(metaEnv.VITE_API_BASE).replace(/\/$/, '')
    : metaEnv.DEV
      ? 'http://127.0.0.1:8000/api/v1'
      : '/api/v1'
);

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
