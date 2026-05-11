// BytePlus TOS upload service.
// Uses pre-signed URL flow: backend issues a PUT URL, frontend uploads directly.
// All endpoints are placeholders — wire to your real backend.

export interface PresignedUrlResponse {
  uploadUrl: string;   // PUT URL with signature
  publicUrl: string;   // Public URL after upload completes
  key: string;         // Object key in the bucket
  expiresAt?: string;
}

export interface PresignRequest {
  filename: string;
  contentType: string;
  size: number;
}

const PRESIGN_ENDPOINT =
  import.meta.env.VITE_TOS_PRESIGN_ENDPOINT ?? "/api/tos/presigned-url";

/** Ask backend for a pre-signed PUT URL. Backend signs with TOS secret keys. */
export async function getPresignedUrl(
  req: PresignRequest,
): Promise<PresignedUrlResponse> {
  const res = await fetch(PRESIGN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Failed to get presigned URL (${res.status})`);
  return (await res.json()) as PresignedUrlResponse;
}

/** Upload file to TOS via PUT with simple retry (network errors only). */
export async function uploadToTOS(
  uploadUrl: string,
  file: File,
  onProgress?: (pct: number) => void,
  retries = 2,
): Promise<void> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      await new Promise<void>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("PUT", uploadUrl);
        xhr.setRequestHeader("Content-Type", file.type);
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable && onProgress) {
            onProgress(Math.round((e.loaded / e.total) * 100));
          }
        };
        xhr.onload = () =>
          xhr.status >= 200 && xhr.status < 300
            ? resolve()
            : reject(new Error(`Upload failed: ${xhr.status}`));
        xhr.onerror = () => reject(new Error("Network error during upload"));
        xhr.send(file);
      });
      return;
    } catch (err) {
      if (attempt === retries) throw err;
      // small backoff
      await new Promise((r) => setTimeout(r, 500 * (attempt + 1)));
    }
  }
}
