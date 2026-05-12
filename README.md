# Vision Analyzer - Audit K3 Otomatis

Project ini adalah aplikasi web untuk melakukan audit visual Alat Pelindung Diri (APD) K3 secara otomatis menggunakan kecerdasan buatan (AI). Aplikasi ini mengintegrasikan **BytePlus TOS** untuk penyimpanan objek dan **BytePlus Seed LLM** untuk analisis gambar terstruktur.

## 🏗️ Struktur Project

Codebase ini menggunakan arsitektur terpisah antara frontend (TanStack Start) dan backend (Flask):

```
cloud-canvas-talk/
├── backend/            # API Flask (Python)
│   ├── services/       # Integrasi TOS & Seed LLM
│   ├── test_images/    # Sampel gambar untuk pengujian K3
│   ├── utils/          # Helper fungsi
│   └── app.py          # Entry point backend
├── src/                # Source code Frontend (React + TanStack)
│   ├── components/     # UI Components (AnalysisResult, Uploader)
│   ├── hooks/          # Logic (useImageAnalysis)
│   └── services/       # API Clients (TOS, LLM)
├── package.json        # Konfigurasi Frontend
├── vite.config.ts      # Konfigurasi Vite & Proxy
└── README.md           # Dokumentasi utama ini
```

## 🚀 Cara Menjalankan

### 1. Persiapan Backend
Masuk ke direktori backend, instal dependensi, dan isi `.env`:
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env # Isi dengan kredensial BytePlus Anda
python app.py
```
Backend akan berjalan di `http://localhost:5000`.

### 2. Persiapan Frontend
Instal dependensi dan jalankan aplikasi dari root directory:
```bash
npm install
npm run dev
```
Frontend akan berjalan di `http://localhost:8080`.

## 🛡️ Keamanan & Privasi
- **Zero Hardcoded Secrets**: Semua kunci API disimpan di file `.env` yang sudah di-exclude oleh `.gitignore`.
- **Private Access**: Gambar diakses melalui *Signed URL* berdurasi terbatas untuk keamanan maksimal.

## 📝 Fitur Unggulan
- **Audit K3 Tanpa Prompt**: Anda hanya perlu upload gambar, sistem secara otomatis menjalankan instruksi audit K3 yang sudah tertanam.
- **Output JSON Terstruktur**: Selain tampilan visual, sistem menyediakan data mentah JSON untuk kebutuhan integrasi sistem lain.
- **Analisis Mendalam**: Mengidentifikasi helm, rompi, sepatu safety, dll., serta memberikan status *Compliant* atau *Non-Compliant*.
- **Deteksi Subjek**: AI akan memberitahu jika tidak ada subjek manusia yang dapat dianalisis dalam gambar.

## 🔗 Integrasi Cloud
- **BytePlus TOS**: Penyimpanan gambar yang aman dan scalable.
- **BytePlus Seed LLM**: Mesin AI vision untuk analisis gambar tingkat lanjut.
