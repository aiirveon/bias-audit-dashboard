const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface AnalyseResult {
  score:       number;
  category:    string;
  confidence:  number;
  shap_values: Record<string, number>;
}

export interface ExplainResult {
  explanation: string;
}

export interface AuditResult {
  total_items:      number;
  flag_rates:       Record<string, number>;
  disparity_ratio:  number;
  fairness_health:  "green" | "amber" | "red";
}

export interface AuditHistoryResult {
  history:  AuditEntry[];
  message?: string;
}

export interface AuditEntry {
  id?:              string;
  created_at?:      string;
  content_snippet?: string;
  category?:        string;
  score?:           number;
  confidence?:      number;
  reviewer_action?: string;
}

export async function analyseContent(content: string): Promise<AnalyseResult> {
  const res = await fetch(`${API_URL}/api/analyse`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`Analyse failed: ${res.status}`);
  return res.json();
}

export async function explainResult(data: {
  content:     string;
  score:       number;
  category:    string;
  confidence:  number;
  shap_values: Record<string, number>;
}): Promise<ExplainResult> {
  const res = await fetch(`${API_URL}/api/explain`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Explain failed: ${res.status}`);
  return res.json();
}

export async function getAuditMetrics(): Promise<AuditResult> {
  const res = await fetch(`${API_URL}/api/audit`);
  if (!res.ok) throw new Error(`Audit failed: ${res.status}`);
  return res.json();
}

export async function getAuditHistory(): Promise<AuditHistoryResult> {
  const res = await fetch(`${API_URL}/api/audit/history`);
  if (!res.ok) throw new Error(`Audit history failed: ${res.status}`);
  return res.json();
}

export async function pingHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
