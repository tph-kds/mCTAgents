const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export async function createRun(problem: string, mode?: string) {
  const resp = await fetch(`${API_URL}/v1/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ problem, mode: mode || "balanced_reasoning" }),
  });
  if (!resp.ok) throw new Error(`Failed to create run: ${resp.statusText}`);
  return resp.json();
}

export async function getRun(runId: string) {
  const resp = await fetch(`${API_URL}/v1/runs/${runId}`);
  if (!resp.ok) throw new Error(`Failed to get run: ${resp.statusText}`);
  return resp.json();
}

export async function getClaims(runId: string) {
  const resp = await fetch(`${API_URL}/v1/runs/${runId}/claims`);
  if (!resp.ok) throw new Error(`Failed to get claims: ${resp.statusText}`);
  return resp.json();
}

export async function getEvidence(runId: string) {
  const resp = await fetch(`${API_URL}/v1/runs/${runId}/evidence`);
  if (!resp.ok) throw new Error(`Failed to get evidence: ${resp.statusText}`);
  return resp.json();
}

export async function cancelRun(runId: string) {
  const resp = await fetch(`${API_URL}/v1/runs/${runId}/cancel`, {
    method: "POST",
  });
  if (!resp.ok) throw new Error(`Failed to cancel run: ${resp.statusText}`);
  return resp.json();
}

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const resp = await fetch(`${API_URL}/v1/documents`, {
    method: "POST",
    body: formData,
  });
  if (!resp.ok) throw new Error(`Failed to upload document: ${resp.statusText}`);
  return resp.json();
}

export async function searchEvidence(query: string, topK?: number) {
  const resp = await fetch(`${API_URL}/v1/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK || 5 }),
  });
  if (!resp.ok) throw new Error(`Failed to search evidence: ${resp.statusText}`);
  return resp.json();
}