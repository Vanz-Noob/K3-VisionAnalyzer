import { useCallback, useRef, useState } from "react";
import { getPresignedUrl, uploadToTOS } from "@/services/tos";
import { analyzeImage } from "@/services/llm";

export type Stage = "idle" | "uploading" | "analyzing" | "done" | "error";

export const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;
export const MAX_SIZE = 5 * 1024 * 1024; // 5MB

export interface ValidationError {
  message: string;
}

export function validateFile(file: File): ValidationError | null {
  if (!ALLOWED_TYPES.includes(file.type as (typeof ALLOWED_TYPES)[number])) {
    return { message: "Format harus JPEG, PNG, atau WEBP." };
  }
  if (file.size > MAX_SIZE) return { message: "Ukuran file maksimal 5MB." };
  return null;
}

export interface UseImageAnalysisState {
  stage: Stage;
  uploadProgress: number;
  imageUrl: string | null;
  result: string | null;
  error: string | null;
}

export function useImageAnalysis() {
  const [state, setState] = useState<UseImageAnalysisState>({
    stage: "idle",
    uploadProgress: 0,
    imageUrl: null,
    result: null,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState({
      stage: "idle",
      uploadProgress: 0,
      imageUrl: null,
      result: null,
      error: null,
    });
  }, []);

  const run = useCallback(async (file: File, prompt: string) => {
    const v = validateFile(file);
    if (v) {
      setState((s) => ({ ...s, stage: "error", error: v.message }));
      throw new Error(v.message);
    }

    setState({
      stage: "uploading",
      uploadProgress: 0,
      imageUrl: null,
      result: null,
      error: null,
    });

    try {
      // 1) Pre-signed URL
      const { uploadUrl, publicUrl } = await getPresignedUrl({
        filename: file.name,
        contentType: file.type,
        size: file.size,
      });

      // 2) Upload directly to TOS
      await uploadToTOS(uploadUrl, file, (pct) =>
        setState((s) => ({ ...s, uploadProgress: pct })),
      );

      setState((s) => ({
        ...s,
        stage: "analyzing",
        imageUrl: publicUrl,
        uploadProgress: 100,
      }));

      // 3) Send URL to LLM
      abortRef.current = new AbortController();
      const res = await analyzeImage(
        { imageUrl: publicUrl, prompt },
        abortRef.current.signal,
      );

      setState((s) => ({ ...s, stage: "done", result: res.content }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setState((s) => ({ ...s, stage: "error", error: message }));
      throw err;
    }
  }, []);

  return { ...state, run, reset };
}
