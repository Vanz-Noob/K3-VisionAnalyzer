import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { ImageUploader } from "@/components/ImageUploader";
import { AnalysisResult } from "@/components/AnalysisResult";
import { useImageAnalysis } from "@/hooks/useImageAnalysis";
import { Loader2, RotateCcw, Sparkles } from "lucide-react";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "Vision Analyzer — Upload & Analisis Gambar dengan AI" },
      {
        name: "description",
        content:
          "Unggah gambar ke BytePlus TOS dan dapatkan analisis cerdas dari LLM secara instan.",
      },
    ],
  }),
});

function Index() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [prompt, setPrompt] = useState(
    "Jelaskan isi gambar ini secara detail dan ringkas.",
  );

  const { stage, uploadProgress, result, error, run, reset } = useImageAnalysis();

  const isWorking = stage === "uploading" || stage === "analyzing";

  const handleAnalyze = async () => {
    if (!file) return;
    try {
      await run(file, prompt);
      toast.success("Analisis selesai");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Terjadi kesalahan");
    }
  };

  const handleReset = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl(null);
    reset();
  };

  return (
    <div className="min-h-screen bg-background">
      <Toaster richColors position="top-right" />

      <header className="border-b border-border">
        <div className="mx-auto flex max-w-4xl items-center gap-3 px-6 py-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">Vision Analyzer</h1>
            <p className="text-xs text-muted-foreground">
              Upload ke BytePlus TOS · Analisis dengan LLM
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl space-y-6 px-6 py-10">
        <ImageUploader
          file={file}
          previewUrl={previewUrl}
          disabled={isWorking}
          onSelect={(f, url) => {
            setFile(f);
            setPreviewUrl(url);
          }}
          onClear={handleReset}
        />

        {file && (
          <div className="space-y-4 rounded-xl border border-border bg-card p-6">
            <div>
              <label className="mb-2 block text-sm font-medium text-foreground">
                Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isWorking}
                rows={3}
                className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-60"
              />
            </div>

            {stage === "uploading" && (
              <div>
                <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                  <span>Mengunggah ke TOS…</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <button
                onClick={handleAnalyze}
                disabled={isWorking || !prompt.trim()}
                className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isWorking ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    {stage === "uploading" ? "Mengunggah…" : "Menganalisis…"}
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Analisis Gambar
                  </>
                )}
              </button>
              <button
                onClick={handleReset}
                disabled={isWorking}
                className="inline-flex items-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-foreground transition hover:bg-accent disabled:opacity-60"
              >
                <RotateCcw className="h-4 w-4" />
                Reset
              </button>
            </div>

            {error && (
              <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </div>
            )}
          </div>
        )}

        <AnalysisResult result={result} loading={stage === "analyzing"} />
      </main>
    </div>
  );
}
