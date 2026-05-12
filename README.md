# Vision Analyzer - Audit K3 Otomatis

Project ini adalah aplikasi web untuk melakukan audit visual Alat Pelindung Diri (APD) K3 secara otomatis menggunakan kecerdasan buatan (AI). Aplikasi ini mengintegrasikan **BytePlus TOS** untuk penyimpanan objek dan **BytePlus Seed LLM** untuk analisis gambar.

## 🏗️ Struktur Project

Codebase telah dirapihkan menjadi dua bagian utama:

```
cloud-canvas-talk/
├── backend/            # API Flask (Python)
│   ├── services/       # Integrasi TOS & LLM
│   ├── test_images/    # Sampel gambar untuk pengujian
│   ├── utils/          # Helper fungsi
│   └── app.py          # Entry point backend
├── frontend/           # Aplikasi React (Vite + TanStack)
│   ├── src/            # Source code frontend
│   └── vite.config.ts  # Konfigurasi proxy ke backend
└── README.md           # Dokumentasi utama
```

## 🚀 Cara Menjalankan

### 1. Persiapan Backend
Masuk ke direktori backend dan instal dependensi:
```bash
cd backend
pip install -r requirements.txt
```
Buat file `.env` berdasarkan `.env.example` dan isi dengan kredensial BytePlus Anda. Lalu jalankan:
```bash
python app.py
```
Backend akan berjalan di `http://localhost:5000`.

### 2. Persiapan Frontend
Masuk ke direktori frontend dan instal dependensi:
```bash
cd frontend
npm install
```
Lalu jalankan aplikasi:
```bash
npm run dev
```
Frontend akan berjalan di `http://localhost:8080`.

## 🛡️ Keamanan
- Semua kunci API dan rahasia harus disimpan di file `.env` (sudah masuk `.gitignore`).
- Jangan pernah melakukan commit file `.env` ke GitHub.
- Gunakan `.env.example` sebagai referensi variabel yang dibutuhkan.

## 📝 Fitur Utama
- **Audit K3 Otomatis**: Mendeteksi helm, rompi, sepatu safety, dll.
- **Deteksi Subjek**: Memberitahu jika tidak ada orang dalam gambar.
- **Status Kepatuhan**: Memberikan penilaian *Compliant* atau *Non-Compliant*.
- **Penyimpanan Cloud**: Integrasi langsung dengan BytePlus TOS.
