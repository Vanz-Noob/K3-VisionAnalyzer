// LLM analysis service. Sends an image URL + prompt to the analyze endpoint.

export interface AnalyzeRequest {
  imageUrl: string;
  prompt: string;
  systemPrompt?: string;
}

export interface AnalyzeResponse {
  content: string;          // markdown / plain text result
  model?: string;
  usage?: { inputTokens?: number; outputTokens?: number };
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

/* Example payload:
   { "imageUrl": "https://bucket.tos-region.bytepluses.com/uploads/xyz.png",
     "prompt": "Describe what you see.",
     "systemPrompt": "You are a helpful vision assistant." }

   Example response:
   { "content": "The image shows ...", "model": "vision-pro",
     "usage": { "inputTokens": 412, "outputTokens": 188 } }
*/
