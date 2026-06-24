#!/bin/bash

# Script untuk menjalankan aplikasi Vision Analyzer
# Menjalankan backend (Flask) dan frontend (Vite) secara bersamaan

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_DIR/.pids"

mkdir -p "$PID_DIR"

echo "====================================="
echo "  Vision Analyzer - Start Application"
echo "====================================="

# Cek apakah aplikasi sudah berjalan
if [ -f "$PID_DIR/backend.pid" ] && kill -0 "$(cat "$PID_DIR/backend.pid")" 2>/dev/null; then
    echo "[WARNING] Backend sudah berjalan (PID: $(cat "$PID_DIR/backend.pid"))"
else
    echo "[1/2] Menjalankan Backend (Flask pada port 5000)..."
    cd "$PROJECT_DIR/backend"
    python3 app.py > "$PID_DIR/backend.log" 2>&1 &
    echo $! > "$PID_DIR/backend.pid"
    sleep 2
    if kill -0 "$(cat "$PID_DIR/backend.pid")" 2>/dev/null; then
        echo "      Backend berjalan (PID: $(cat "$PID_DIR/backend.pid"))"
    else
        echo "      [ERROR] Backend gagal berjalan. Cek log: $PID_DIR/backend.log"
        cat "$PID_DIR/backend.log"
        exit 1
    fi
fi

if [ -f "$PID_DIR/frontend.pid" ] && kill -0 "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null; then
    echo "[WARNING] Frontend sudah berjalan (PID: $(cat "$PID_DIR/frontend.pid"))"
else
    echo "[2/2] Menjalankan Frontend (Vite pada port 8080)..."
    cd "$PROJECT_DIR"
    npm run dev > "$PID_DIR/frontend.log" 2>&1 &
    echo $! > "$PID_DIR/frontend.pid"
    sleep 3
    if kill -0 "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null; then
        echo "      Frontend berjalan (PID: $(cat "$PID_DIR/frontend.pid"))"
    else
        echo "      [ERROR] Frontend gagal berjalan. Cek log: $PID_DIR/frontend.log"
        cat "$PID_DIR/frontend.log"
        exit 1
    fi
fi

echo ""
echo "====================================="
echo "  Aplikasi berhasil dijalankan!"
echo "  Backend  : http://localhost:5000"
echo "  Frontend : http://localhost:8080"
echo "====================================="
echo "  Untuk mematikan, jalankan: ./stop.sh"
echo "  Untuk cek log:"
echo "    Backend  : cat $PID_DIR/backend.log"
echo "    Frontend : cat $PID_DIR/frontend.log"
echo "====================================="
