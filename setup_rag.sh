#!/bin/bash
#
# RAG System Setup Script for macOS
# Installs all dependencies and configures the RAG system
#

set -e  # Exit on error

echo "=========================================="
echo "🚀 Marker RAG System Setup (macOS)"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}This script is designed for macOS. Adjust commands for your OS.${NC}"
    exit 1
fi

# 1. Check Python
echo -e "${YELLOW}Step 1: Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo

# 2. Setup Backend Virtual Environment
echo -e "${YELLOW}Step 2: Setting up backend virtual environment...${NC}"
cd "$(dirname "$0")"
BACKEND_DIR="$(pwd)"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo

# 3. Upgrade pip
echo -e "${YELLOW}Step 3: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"
echo

# 4. Install main dependencies
echo -e "${YELLOW}Step 4: Installing main dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Main dependencies installed${NC}"
else
    echo -e "${YELLOW}requirements.txt not found, skipping${NC}"
fi
echo

# 5. Install RAG-specific dependencies
echo -e "${YELLOW}Step 5: Installing RAG system dependencies...${NC}"
pip install -r requirements-rag.txt
echo -e "${GREEN}✓ RAG dependencies installed${NC}"
echo

# 6. Install Ollama (if not already installed)
echo -e "${YELLOW}Step 6: Checking Ollama installation...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found. Would you like to install it? (y/n)${NC}"
    read -r INSTALL_OLLAMA
    if [[ $INSTALL_OLLAMA == "y" || $INSTALL_OLLAMA == "Y" ]]; then
        echo "Installing Ollama using Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}Homebrew not found. Please install from https://brew.sh${NC}"
        else
            brew install ollama
            echo -e "${GREEN}✓ Ollama installed${NC}"
            echo "Starting Ollama service..."
            brew services start ollama
            echo -e "${GREEN}✓ Ollama service started${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Ollama required for LLM features. Visit: https://ollama.ai${NC}"
    fi
else
    echo -e "${GREEN}✓ Ollama found${NC}"
fi
echo

# 7. Pull a default model
echo -e "${YELLOW}Step 7: Checking Ollama models...${NC}"
sleep 2  # Give Ollama time to start
if command -v ollama &> /dev/null; then
    echo "Available Ollama models:"
    ollama list 2>/dev/null || echo "(run 'ollama list' in another terminal)"
    
    echo
    echo "Recommended models (pull one of these):"
    echo "  - ollama pull gemma2:2b      (smallest, fastest)"
    echo "  - ollama pull llama2:7b      (balanced)"
    echo "  - ollama pull llama3:8b      (best quality)"
    echo
    echo "To pull a model, run: ollama pull <model-name>"
fi
echo

# 8. Setup Node.js / Frontend (optional)
echo -e "${YELLOW}Step 8: Frontend setup (optional)${NC}"
echo "Would you like to setup the React frontend? (y/n)"
read -r SETUP_FRONTEND
if [[ $SETUP_FRONTEND == "y" || $SETUP_FRONTEND == "Y" ]]; then
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}Node.js not found. Installing with Homebrew...${NC}"
        brew install node
    fi
    
    cd "$BACKEND_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    fi
fi
echo

# 9. Display instructions
echo
echo -e "${GREEN}=========================================="
echo "✓ Setup Complete!"
echo "==========================================${NC}"
echo
echo "📖 Next steps:"
echo
echo "1. Start Ollama (if using LLM features):"
echo "   brew services start ollama"
echo "   # Then in another terminal:"
echo "   ollama pull gemma2:2b"
echo
echo "2. Start the backend server:"
cd backend
echo "   source venv/bin/activate"
echo "   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
echo
echo "3. (Optional) Start the frontend:"
echo "   cd ../frontend"
echo "   npm run dev"
echo
echo "4. Access the application:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173 (or http://localhost:3000)"
echo
echo "5. Try the RAG endpoints:"
echo "   Health check: curl http://localhost:8000/api/rag/health"
echo "   Config: curl http://localhost:8000/api/rag/config"
echo
echo -e "${YELLOW}⚠️  Important: Some components require Ollama running in background${NC}"
echo
