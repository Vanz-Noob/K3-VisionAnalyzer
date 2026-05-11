import ReactMarkdown from "react-markdown";
import { Sparkles } from "lucide-react";

interface Props {
  result: string | null;
  loading: boolean;
}

export function AnalysisResult({ result, loading }: Props) {
  if (!result && !loading) return null;

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Sparkles className="h-4 w-4 text-primary" />
        Hasil Analisis
      </div>

      {loading ? (
        <div className="space-y-2">
          <div className="h-3 w-3/4 animate-pulse rounded bg-muted" />
          <div className="h-3 w-full animate-pulse rounded bg-muted" />
          <div className="h-3 w-5/6 animate-pulse rounded bg-muted" />
          <div className="h-3 w-2/3 animate-pulse rounded bg-muted" />
        </div>
      ) : (
        <div className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-strong:text-foreground prose-code:text-foreground">
          <ReactMarkdown>{result ?? ""}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
