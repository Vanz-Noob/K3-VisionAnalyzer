/// <reference types="vite/client" />
// LLM analysis service. Sends an image URL + prompt to the analyze endpoint.

export interface PPEItem {
  name: string;
  worn: boolean;
}

export interface IndividualAnalysis {
  id: number;
  ppeItems: PPEItem[];
  compliance: "Compliant" | "Non-Compliant";
  missingItems: string[];
  recommendation: string;
}

export interface K3Analysis {
  hasSubject: boolean | null;
  individuals: IndividualAnalysis[];
  overallCompliance: "Compliant" | "Non-Compliant" | "N/A";
  summary: string;
}

export interface AnalyzeRequest {
  imageUrl: string;
  prompt: string;
  systemPrompt?: string;
}

export interface AnalyzeResponse {
  content: string;
  analysis: K3Analysis;
  model?: string;
  usage?: { inputTokens?: number; outputTokens?: number; totalTokens?: number };
}

const LLM_ENDPOINT =
  import.meta.env.VITE_LLM_ANALYZE_ENDPOINT ?? "/api/llm/analyze";

export async function analyzeImage(
  req: AnalyzeRequest,
  signal?: AbortSignal,
): Promise<AnalyzeResponse> {
  const res = await fetch(LLM_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`LLM request failed (${res.status}): ${text}`);
  }
  return (await res.json()) as AnalyzeResponse;
}
