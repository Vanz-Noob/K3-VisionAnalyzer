/// <reference types="vite/client" />
import { useCallback, useRef, useState } from "react";
import { getPresignedUrl, uploadToTOS } from "@/services/tos";
import { analyzeImage, type K3Analysis } from "@/services/llm";

const UPLOAD_COMPLETE_ENDPOINT =
  import.meta.env.VITE_UPLOAD_COMPLETE_ENDPOINT ?? "/api/tos/upload-complete";

async function notifyUploadComplete(key: string, filename: string) {
  const res = await fetch(UPLOAD_COMPLETE_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, filename }),
  });
  if (!res.ok) {
    throw new Error(`Failed to notify upload complete (${res.status})`);
  }
  return await res.json();
}

export type Stage = "idle" | "uploading" | "analyzing" | "done" | "error";

export const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;
export const MAX_SIZE = 5 * 1024 * 1024;

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
  key: string | null;
  imageUrl: string | null;
  result: string | null;
  analysis: K3Analysis | null;
  error: string | null;
}

export function useImageAnalysis() {
  const [state, setState] = useState<UseImageAnalysisState>({
    stage: "idle",
    uploadProgress: 0,
    key: null,
    imageUrl: null,
    result: null,
    analysis: null,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState({
      stage: "idle",
      uploadProgress: 0,
      key: null,
      imageUrl: null,
      result: null,
      analysis: null,
      error: null,
    });
  }, []);

  const run = useCallback(async (file: File) => {
    const v = validateFile(file);
    if (v) {
      setState((s) => ({ ...s, stage: "error", error: v.message }));
      throw new Error(v.message);
    }

    setState({
      stage: "uploading",
      uploadProgress: 0,
      key: null,
      imageUrl: null,
      result: null,
      analysis: null,
      error: null,
    });

    try {
      const { uploadUrl, publicUrl, key } = await getPresignedUrl({
        filename: file.name,
        contentType: file.type,
        size: file.size,
      });

      await uploadToTOS(uploadUrl, file, (pct: number) =>
        setState((s) => ({ ...s, uploadProgress: pct })),
      );

      await notifyUploadComplete(key, file.name);

      setState((s) => ({
        ...s,
        stage: "analyzing",
        key: key,
        imageUrl: publicUrl,
        uploadProgress: 100,
      }));

      abortRef.current = new AbortController();
      const res = await analyzeImage(
        { imageUrl: publicUrl, prompt: "" },
        abortRef.current.signal,
      );

      setState((s) => ({
        ...s,
        stage: "done",
        result: res.content,
        analysis: res.analysis ?? null,
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setState((s) => ({ ...s, stage: "error", error: message }));
      throw err;
    }
  }, []);

  return { ...state, run, reset };
}