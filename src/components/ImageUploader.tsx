import { useCallback, useRef, useState } from "react";
import { ImageIcon, UploadCloud, X } from "lucide-react";
import { ALLOWED_TYPES, MAX_SIZE, validateFile } from "@/hooks/useImageAnalysis";
import { toast } from "sonner";

interface Props {
  file: File | null;
  previewUrl: string | null;
  onSelect: (file: File, previewUrl: string) => void;
  onClear: () => void;
  disabled?: boolean;
}

export function ImageUploader({ file, previewUrl, onSelect, onClear, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (f: File) => {
      const err = validateFile(f);
      if (err) {
        toast.error(err.message);
        return;
      }
      onSelect(f, URL.createObjectURL(f));
    },
    [onSelect],
  );

  return (
    <div className="w-full">
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(",")}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
          e.target.value = "";
        }}
      />

      {previewUrl ? (
        <div className="relative overflow-hidden rounded-xl border border-border bg-card">
          <img src={previewUrl} alt="preview" className="max-h-96 w-full object-contain" />
          {!disabled && (
            <button
              onClick={onClear}
              className="absolute right-3 top-3 rounded-full bg-background/80 p-2 text-foreground backdrop-blur transition hover:bg-background"
              aria-label="Hapus gambar"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          {file && (
            <div className="flex items-center justify-between gap-2 border-t border-border bg-muted/40 px-4 py-2 text-sm text-muted-foreground">
              <span className="flex items-center gap-2 truncate">
                <ImageIcon className="h-4 w-4 shrink-0" />
                <span className="truncate">{file.name}</span>
              </span>
              <span>{(file.size / 1024).toFixed(1)} KB</span>
            </div>
          )}
        </div>
      ) : (
        <button
          type="button"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            const f = e.dataTransfer.files?.[0];
            if (f) handleFile(f);
          }}
          className={`flex w-full flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-6 py-16 text-center transition ${
            dragOver
              ? "border-primary bg-primary/5"
              : "border-border bg-card hover:border-primary/60 hover:bg-muted/50"
          } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
        >
          <UploadCloud className="h-10 w-10 text-muted-foreground" />
          <div>
            <p className="font-medium text-foreground">
              Tarik & lepas gambar, atau klik untuk memilih
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              JPEG, PNG, WEBP — maks {MAX_SIZE / 1024 / 1024}MB
            </p>
          </div>
        </button>
      )}
    </div>
  );
}
