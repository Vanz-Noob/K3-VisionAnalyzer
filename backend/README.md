# Vision Analyzer Backend

Flask backend untuk aplikasi Vision Analyzer dengan integrasi BytePlus TOS dan Seed LLM yang berfokus pada Audit K3 Otomatis.

## 🚀 Fitur Backend

- ✅ **Audit K3 Otomatis**: Menggunakan prompt tetap untuk analisis APD (helm, rompi, sepatu, dll).
- ✅ **JSON Output**: Menghasilkan data analisis terstruktur yang mudah diparsing oleh frontend.
- ✅ **Deteksi Subjek**: Logika cerdas untuk mendeteksi keberadaan orang dalam gambar.
- ✅ **TOS Integration**: Pembuatan *Pre-signed URL* untuk upload dan *Signed URL* untuk akses aman.
- ✅ **CORS Managed**: Konfigurasi otomatis pada bucket TOS untuk mengizinkan request dari frontend.

## 📡 API Endpoints

### 1. Health Check
`GET /health` -> Memastikan server backend aktif.

### 2. Generate Pre-signed URL
`POST /api/tos/presigned-url`
- **Request**: `{"filename": "test.jpg", "contentType": "image/jpeg", "size": 1234}`
- **Response**: Mengembalikan URL untuk pengunggahan langsung ke TOS.

### 3. Upload Complete
`POST /api/tos/upload-complete`
- **Request**: `{"key": "uploads/xyz.jpg", "filename": "test.jpg"}`
- **Response**: Mencatat link publik ke dalam file `.txt` di folder `temp/`.

### 4. Analyze Image (K3 Audit)
`POST /api/llm/analyze`
- **Request**: `{"imageUrl": "https://..."}`
- **Response**: Mengembalikan hasil analisis teks dan objek JSON terstruktur.
  ```json
  {
    "analysis": {
      "hasSubject": true,
      "individuals": [...],
      "overallCompliance": "Compliant",
      "summary": "..."
    },
    "content": "Analisis teks lengkap...",
    "model": "seed-2-0-code-preview-260328"
  }
  ```

## 🔧 Konfigurasi (.env)

Pastikan file `.env` di direktori ini berisi:
```env
TOS_ACCESS_KEY_ID=...
TOS_SECRET_ACCESS_KEY=...
TOS_REGION=...
TOS_BUCKET=...
TOS_ENDPOINT=...

ARK_API_KEY=...
ARK_MODEL=seed-2-0-code-preview-260328
```

## 📁 Struktur Folder

```
backend/
├── services/
│   ├── tos_service.py   # Logika BytePlus TOS
│   └── llm_service.py   # Logika Seed LLM & Prompt K3
├── utils/
│   └── file_utils.py    # Utilitas penyimpanan lokal
├── test_images/         # Gambar contoh untuk pengujian K3
└── app.py               # Entry point Flask API
```

## 🏃 Cara Menjalankan
```bash
pip install -r requirements.txt
python app.py
```
Server akan berjalan di `http://localhost:5000`.
