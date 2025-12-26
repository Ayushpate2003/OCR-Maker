#!/bin/bash

# Marker Web Application - Quick Start Script
# This script sets up and runs both backend and frontend

set -e

echo "🚀 Marker Web Application Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [[ "$PYTHON_VERSION" != "3.10" && "$PYTHON_VERSION" != "3.11" && "$PYTHON_VERSION" != "3.12" ]]; then
    echo -e "${RED}Error: Python 3.10, 3.11, or 3.12 required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Check Node.js
echo -e "\n${YELLOW}Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js not found. Install from https://nodejs.org${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION detected${NC}"

# Backend setup
echo -e "\n${YELLOW}Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Check if marker is installed
if ! command -v marker &> /dev/null; then
    echo "Installing marker-pdf..."
    pip install "marker-pdf[full]" --quiet
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Frontend setup
cd ../frontend
echo -e "\n${YELLOW}Setting up Frontend...${NC}"

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --silent
else
    echo "node_modules already exists, skipping npm install"
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

# Check Ollama
cd ..
echo -e "\n${YELLOW}Checking Ollama (optional)...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama detected${NC}"
    
    # Check if ollama is running
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ollama service is running${NC}"
    else
        echo -e "${YELLOW}⚠ Ollama installed but not running${NC}"
        echo -e "  Start it with: ${GREEN}ollama serve${NC}"
        echo -e "  Then pull a model: ${GREEN}ollama pull gemma2:2b${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Ollama not installed (LLM features disabled)${NC}"
    echo -e "  Install from: https://ollama.com"
fi

# Create startup script
echo -e "\n${YELLOW}Creating startup scripts...${NC}"

# Backend start script
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
echo "🔧 Starting Backend on http://localhost:8000"
python main.py
EOF
chmod +x start-backend.sh

# Frontend start script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
echo "🎨 Starting Frontend on http://localhost:3000"
npm run dev
EOF
chmod +x start-frontend.sh

# Combined start script
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Marker Web Application"
echo "=================================="
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF
chmod +x start.sh

echo -e "${GREEN}✓ Startup scripts created${NC}"

# Summary
echo -e "\n${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Setup Complete! 🎉                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}To start the application:${NC}"
echo ""
echo -e "  ${GREEN}./start.sh${NC}          # Start both backend and frontend"
echo ""
echo -e "${YELLOW}Or start separately:${NC}"
echo ""
echo -e "  ${GREEN}./start-backend.sh${NC}  # Backend only (port 8000)"
echo -e "  ${GREEN}./start-frontend.sh${NC} # Frontend only (port 3000)"
echo ""
echo -e "${YELLOW}Then open:${NC} ${GREEN}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Optional (for LLM features):${NC}"
echo -e "  ${GREEN}ollama serve${NC}        # Start Ollama"
echo -e "  ${GREEN}ollama pull gemma2:2b${NC} # Download model"
echo ""
