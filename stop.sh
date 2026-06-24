#!/bin/bash

# Script untuk mematikan aplikasi Vision Analyzer
# Menghentikan backend (Flask) dan frontend (Vite)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_DIR/.pids"

echo "====================================="
echo "  Vision Analyzer - Stop Application"
echo "====================================="

STOPPED=0

# Matikan Backend
if [ -f "$PID_DIR/backend.pid" ]; then
    PID=$(cat "$PID_DIR/backend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[1/2] Mematikan Backend (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 1
        # Force kill jika masih berjalan
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
        fi
        echo "      Backend berhasil dimatikan."
        rm -f "$PID_DIR/backend.pid"
        STOPPED=1
    else
        echo "[1/2] Backend sudah tidak berjalan."
        rm -f "$PID_DIR/backend.pid"
    fi
else
    echo "[1/2] Backend tidak ditemukan (belum dijalankan via start.sh)."
    # Fallback: cari proses Flask pada port 5000
    FLASK_PID=$(lsof -ti:5000 2>/dev/null)
    if [ -n "$FLASK_PID" ]; then
        echo "      Menemukan proses pada port 5000 (PID: $FLASK_PID), mematikan..."
        kill "$FLASK_PID" 2>/dev/null
        echo "      Proses pada port 5000 berhasil dimatikan."
        STOPPED=1
    fi
fi

# Matikan Frontend
if [ -f "$PID_DIR/frontend.pid" ]; then
    PID=$(cat "$PID_DIR/frontend.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[2/2] Mematikan Frontend (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 1
        # Force kill jika masih berjalan
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
        fi
        echo "      Frontend berhasil dimatikan."
        rm -f "$PID_DIR/frontend.pid"
        STOPPED=1
    else
        echo "[2/2] Frontend sudah tidak berjalan."
        rm -f "$PID_DIR/frontend.pid"
    fi
else
    echo "[2/2] Frontend tidak ditemukan (belum dijalankan via start.sh)."
    # Fallback: cari proses Vite pada port 8080
    VITE_PID=$(lsof -ti:8080 2>/dev/null)
    if [ -n "$VITE_PID" ]; then
        echo "      Menemukan proses pada port 8080 (PID: $VITE_PID), mematikan..."
        kill "$VITE_PID" 2>/dev/null
        echo "      Proses pada port 8080 berhasil dimatikan."
        STOPPED=1
    fi
fi

if [ $STOPPED -eq 0 ]; then
    echo ""
    echo "  Tidak ada proses yang perlu dimatikan."
else
    echo ""
    echo "  Semua proses berhasil dimatikan."
fi

echo "====================================="
