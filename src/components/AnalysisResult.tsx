import ReactMarkdown from "react-markdown";
import { Sparkles, CheckCircle2, XCircle, AlertTriangle, FileJson } from "lucide-react";
import type { K3Analysis, IndividualAnalysis } from "@/services/llm";

interface Props {
  result: string | null;
  analysis: K3Analysis | null;
  loading: boolean;
}

function ComplianceBadge({ status }: { status: string }) {
  if (status === "Compliant") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
        <CheckCircle2 className="h-3 w-3" />
        Compliant
      </span>
    );
  }
  if (status === "Non-Compliant") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
        <XCircle className="h-3 w-3" />
        Non-Compliant
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
      N/A
    </span>
  );
}

function PPEItemRow({ name, worn }: { name: string; worn: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-md border border-border px-3 py-1.5 text-sm">
      <span>{name}</span>
      {worn ? (
        <CheckCircle2 className="h-4 w-4 text-green-600" />
      ) : (
        <XCircle className="h-4 w-4 text-red-500" />
      )}
    </div>
  );
}

function IndividualCard({
  individual,
}: {
  individual: K3Analysis["individuals"][number];
}) {
  return (
    <div className="rounded-lg border border-border bg-background p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-semibold text-foreground">
          Orang #{individual.id}
        </span>
        <ComplianceBadge status={individual.compliance} />
      </div>

      <div className="mb-3 grid grid-cols-2 gap-1.5 sm:grid-cols-3">
        {individual.ppeItems.map((item, i: number) => (
          <PPEItemRow key={i} name={item.name} worn={item.worn} />
        ))}
      </div>

      {individual.missingItems.length > 0 && (
        <div className="mb-2 flex items-start gap-1.5 rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>
            <strong>Kurang:</strong> {individual.missingItems.join(", ")}
          </span>
        </div>
      )}

      {individual.recommendation && (
        <p className="text-xs text-muted-foreground">
          💡 {individual.recommendation}
        </p>
      )}
    </div>
  );
}

export function AnalysisResult({ result, analysis, loading }: Props) {
  if (!result && !loading) return null;

  return (
    <div className="space-y-4">
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
        ) : analysis && analysis.hasSubject === false ? (
          <div className="flex items-center gap-2 rounded-md bg-amber-50 px-4 py-3 text-sm text-amber-800">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {analysis.summary}
          </div>
        ) : analysis && analysis.hasSubject === true ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {analysis.summary}
              </span>
              <ComplianceBadge status={analysis.overallCompliance} />
            </div>

            <div className="space-y-3">
              {analysis.individuals.map((ind: IndividualAnalysis) => (
                <IndividualCard key={ind.id} individual={ind} />
              ))}
            </div>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-strong:text-foreground prose-code:text-foreground">
            <ReactMarkdown>{result ?? ""}</ReactMarkdown>
          </div>
        )}
      </div>

      {analysis ? (
        <div className="rounded-xl border-2 border-primary/20 bg-card overflow-hidden shadow-sm">
          <div className="flex items-center justify-between border-b border-border bg-primary/5 px-6 py-3">
            <div className="flex items-center gap-2">
              <FileJson className="h-4 w-4 text-primary" />
              <span className="text-sm font-bold text-foreground uppercase tracking-wider">Data Terstruktur (JSON)</span>
            </div>
            <span className="text-[10px] font-mono text-muted-foreground bg-muted px-2 py-0.5 rounded">application/json</span>
          </div>
          <div className="p-0">
            <pre className="max-h-[500px] overflow-auto p-4 text-[13px] leading-relaxed text-blue-700 font-mono bg-white">
              {JSON.stringify(analysis, null, 2)}
            </pre>
          </div>
        </div>
      ) : (
        !loading && result && (
          <div className="rounded-xl border border-dashed border-border p-4 text-center text-xs text-muted-foreground">
            Data JSON tidak tersedia untuk hasil ini.
          </div>
        )
      )}
    </div>
  );
}
