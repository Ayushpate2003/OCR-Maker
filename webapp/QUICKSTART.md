# 🚀 Quick Start Guide

## 1. Automated Setup (Recommended)

```bash
cd webapp
chmod +x setup.sh
./setup.sh
```

This will:
- Check Python and Node.js versions
- Create Python virtual environment
- Install all dependencies
- Create startup scripts

## 2. Start the Application

```bash
./start.sh
```

Or start services separately:
```bash
./start-backend.sh   # Terminal 1
./start-frontend.sh  # Terminal 2
```

## 3. Optional: Start Ollama (for LLM features)

```bash
# Terminal 3
ollama serve

# Pull a model (first time only)
ollama pull gemma2:2b
```

## 4. Open Browser

Navigate to: **http://localhost:3000**

---

## Manual Setup

If you prefer manual setup:

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "marker-pdf[full]"
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## First Conversion

1. Drag & drop a PDF file
2. (Optional) Enable "LLM Enhancement" and select model
3. Choose output format (Markdown recommended)
4. Click "Start Conversion"
5. View results in the right panel
6. Download individual files or all at once

---

## Troubleshooting

**Backend fails to start:**
- Ensure Python 3.10-3.12 is installed
- Activate virtual environment: `source backend/venv/bin/activate`
- Verify marker CLI: `marker --help`

**Frontend fails to start:**
- Ensure Node.js 18+ is installed
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**LLM mode not working:**
- Start Ollama: `ollama serve`
- Pull model: `ollama pull gemma2:2b`
- Check Ollama is running: `curl http://localhost:11434/api/version`

**Conversion fails:**
- Check backend terminal for errors
- Try without LLM mode first
- Ensure file is a valid PDF
- Check file size (max 100MB by default)

---

For detailed documentation, see [README.md](README.md)
