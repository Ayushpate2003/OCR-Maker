#!/bin/bash

# ============================================
# RAG Project - Service Restart Script
# ============================================

set -e

MARKER_DIR="/Volumes/Volume A/project V1/marker"
BACKEND_DIR="$MARKER_DIR/webapp/backend"
FRONTEND_DIR="$MARKER_DIR/webapp/frontend"

echo "🔄 Restarting RAG Project Services..."
echo ""

# ============================================
# 1. Stop Existing Services
# ============================================
echo "🛑 Stopping existing services..."

# Kill backend (uvicorn)
pkill -f "uvicorn main:app" 2>/dev/null || echo "  Backend not running"

# Kill frontend (npm/vite)
pkill -f "vite" 2>/dev/null || echo "  Frontend not running"

# Note: We don't kill Ollama as it's a system service
echo "  ✓ Services stopped"
echo ""

# Wait for ports to be released
sleep 2

# ============================================
# 2. Check Ollama Status
# ============================================
echo "🤖 Checking Ollama..."
if pgrep -x "ollama" > /dev/null; then
    echo "  ✓ Ollama is running"
else
    echo "  ⚠️  Ollama not running. Starting..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo "  ✓ Ollama started"
fi
echo ""

# ============================================
# 3. Start Backend
# ============================================
echo "🚀 Starting Backend (FastAPI)..."
cd "$BACKEND_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "  ✓ Virtual environment activated"
else
    echo "  ❌ Virtual environment not found. Run setup_rag.sh first"
    exit 1
fi

# Start backend in background
nohup python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload > /tmp/rag_backend.log 2>&1 &
BACKEND_PID=$!
echo "  ✓ Backend started (PID: $BACKEND_PID)"
echo "  📍 http://localhost:8000"
echo ""

# Wait for backend to be ready
sleep 3

# ============================================
# 4. Test Backend Health
# ============================================
echo "🏥 Testing Backend Health..."
if curl -s http://localhost:8000/api/rag/health > /dev/null 2>&1; then
    echo "  ✓ Backend is healthy"
else
    echo "  ⚠️  Backend health check failed (may need more time)"
fi
echo ""

# ============================================
# 5. Start Frontend (Optional)
# ============================================
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    echo "🎨 Starting Frontend (React)..."
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "  📦 Installing dependencies..."
        npm install
    fi
    
    # Start frontend in background
    nohup npm run dev > /tmp/rag_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "  ✓ Frontend started (PID: $FRONTEND_PID)"
    echo "  📍 http://localhost:5173 (or 3000)"
    echo ""
else
    echo "⏭️  Frontend directory not found - skipping"
    echo ""
fi

# ============================================
# 6. Summary
# ============================================
echo "✅ RAG Project Services Restarted!"
echo ""
echo "═══════════════════════════════════════"
echo "📊 Service Status:"
echo "═══════════════════════════════════════"
echo ""
echo "🤖 Ollama:   http://localhost:11434"
echo "   Status:   $(pgrep -x "ollama" > /dev/null && echo "✅ Running" || echo "❌ Stopped")"
echo ""
echo "🔧 Backend:  http://localhost:8000"
echo "   PID:      $BACKEND_PID"
echo "   Logs:     tail -f /tmp/rag_backend.log"
echo "   Health:   curl http://localhost:8000/api/rag/health"
echo ""
if [ -n "$FRONTEND_PID" ]; then
    echo "🎨 Frontend: http://localhost:5173"
    echo "   PID:      $FRONTEND_PID"
    echo "   Logs:     tail -f /tmp/rag_frontend.log"
    echo ""
fi
echo "═══════════════════════════════════════"
echo ""
echo "🎯 Quick Commands:"
echo ""
echo "# Check backend logs:"
echo "tail -f /tmp/rag_backend.log"
echo ""
echo "# Check frontend logs:"
echo "tail -f /tmp/rag_frontend.log"
echo ""
echo "# Test API:"
echo "curl http://localhost:8000/api/rag/health | jq"
echo ""
echo "# Stop all services:"
echo "pkill -f 'uvicorn main:app'"
echo "pkill -f 'vite'"
echo ""
echo "═══════════════════════════════════════"
echo ""
echo "🎉 Ready to use!"
echo ""
