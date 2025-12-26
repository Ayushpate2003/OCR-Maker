# Marker Web Application

A modern, responsive web interface for the [Marker](https://github.com/VikParuchuri/marker) document conversion tool. Convert PDFs and documents to Markdown, JSON, and HTML with optional LLM-powered enhancement using Ollama.

**Status**: ✅ Production-ready | Tested on macOS with Python 3.11, Node.js 18+, Ollama 0.13+

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Quick Start (5 minutes)](#quick-start-5-minutes)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
- [Production Deployment](#production-deployment)
- [License](#license)

## Features

✨ **Drag & Drop Upload** - Easy multi-file upload with visual feedback  
🤖 **LLM Enhancement** - Optional Ollama integration for higher accuracy  
📊 **Multiple Output Formats** - Markdown, JSON, HTML, and Chunks  
🎨 **Modern UI** - Clean, responsive Tailwind CSS design  
📈 **Real-time Progress** - Live conversion status tracking  
👁️ **Live Preview** - View results directly in browser with syntax highlighting  
📦 **Batch Processing** - Convert multiple files simultaneously  
💾 **Easy Downloads** - Download individual files or entire job results  
🔍 **Job History** - Track all conversion jobs with error details  

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React 18 + Vite + Tailwind CSS |
| **Backend** | FastAPI (Python 3.11) |
| **Document Processing** | Marker CLI |
| **LLM (Optional)** | Ollama (local models) |
| **HTTP Client** | Axios |
| **Markdown Rendering** | React Markdown |

## System Requirements

### Minimum

- **OS**: macOS, Linux, or Windows (WSL2)
- **Python**: 3.10, 3.11, or **3.12** (NOT 3.13+)  
  ⚠️ **Important**: Use 3.11+ for best compatibility with Marker
- **Node.js**: 18+ (for frontend)
- **RAM**: 4GB (8GB+ recommended for LLM mode)
- **Disk**: 5GB free (models require additional space)

### Optional

- **Ollama**: For LLM-enhanced conversion (Ollama 0.13+)
- **GPU**: NVIDIA CUDA or Apple Silicon MPS for faster processing

## Quick Start (5 minutes)

### Prerequisites

```bash
# Check Python version (must be 3.10–3.12)
python3 --version

# Check Node.js (must be 18+)
node --version

# macOS: Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### One-Command Setup

```bash
cd /path/to/marker/webapp
chmod +x setup.sh
./setup.sh
```

The setup script will automatically:
1. Verify Python version (3.10–3.12)
2. Create Python virtual environment
3. Install backend dependencies (FastAPI, Marker, psutil)
4. Install frontend dependencies (React, Tailwind, etc.)
5. Create startup scripts
6. Check for Ollama availability

### Start Services

```bash
# Option 1: Start both services in separate terminals
Terminal 1: ./start-backend.sh   # Backend on http://localhost:8000
Terminal 2: ./start-frontend.sh  # Frontend on http://localhost:3000

# Option 2: Start everything together
./start.sh

# Option 3: Manual startup
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend:
cd frontend && npm run dev

# Terminal 3 - Ollama (optional, for LLM):
ollama serve
```

### Open Browser

Navigate to: **http://localhost:3000**

## Installation

### Backend Setup (Python)

```bash
cd /path/to/marker/webapp/backend

# Create virtual environment (Python 3.11 recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version
python -V  # Should show 3.11.x or similar

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Backend Dependencies** (`requirements.txt`):
```
fastapi==0.115.4          # API framework
uvicorn[standard]==0.32.0 # ASGI server
python-multipart==0.0.16  # File upload parsing
pydantic==2.12.5          # ⚠️ IMPORTANT: >=2.7.1 for Marker compatibility
psutil==5.9.8            # ⚠️ REQUIRED: Used by Marker CLI
```

### Frontend Setup (Node.js)

```bash
cd /path/to/marker/webapp/frontend

# Install dependencies
npm install

# Verify build (optional)
npm run build
```

**Key Dependencies** (`package.json`):
- React 18, React DOM
- Vite 5 (build tool)
- Tailwind CSS 3 + @tailwindcss/typography (for prose styling)
- Axios (HTTP client)
- React Markdown, React Dropzone, Lucide React

### Ollama Setup (Optional - for LLM features)

```bash
# Install Ollama
brew install ollama  # macOS
# Or download from https://ollama.com for other systems

# Start Ollama background service (preferred)
brew services start ollama

# Or run in foreground (separate terminal)
ollama serve

# Pull a model (first time only)
ollama pull gemma2:2b
# Other models: llama3.2-vision, llama3:8b, mistral:7b, qwen2.5:7b

# Verify API is running
curl -sS http://localhost:11434/api/version
```

## Running the Application

### Development Mode

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
- Backend API: http://127.0.0.1:8000
- Swagger Docs: http://127.0.0.1:8000/docs

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```
- Frontend: http://localhost:3000 (proxies to backend)

**Terminal 3 - Ollama** (if using LLM):
```bash
ollama serve
# API: http://localhost:11434
```

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Serve built files
npm install -g serve
serve -s dist -p 3000

# Backend (production ASGI server)
cd ../backend
source venv/bin/activate
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Usage Guide

### Basic Workflow

1. **Upload Files**
   - Drag & drop PDF/image files onto upload area
   - Or click to browse
   - Supported: PDF, PNG, JPG, JPEG, TIFF, BMP
   - Max: 100MB per file

2. **Configure Conversion**
   - **Output Format**: Markdown (default), JSON, HTML, or Chunks
   - **Enable LLM**: Toggle for AI-enhanced accuracy
   - **Ollama Model**: Select from available models (if LLM enabled)
   - **Force OCR**: Re-OCR all text (useful for scanned PDFs)

3. **Start Conversion**
   - Click "Start Conversion" button
   - Watch real-time progress bar
   - Job added to "Conversion Jobs" sidebar

4. **View & Download Results**
   - Click a job to view its results
   - **Preview tab**: View markdown/JSON/HTML in browser
   - **Files tab**: List all output files with download links
   - **Images tab**: Gallery of extracted images
   - **Raw tab**: Debug job metadata
   - Download individual files or batch download

### Output Formats

| Format | Best For | Contents |
|--------|----------|----------|
| **Markdown** | Default, humans | Text, tables, code, LaTeX equations |
| **JSON** | RAG, data extraction | Structured block hierarchy, bounding boxes |
| **HTML** | Web publishing | Styled HTML with embedded images |
| **Chunks** | RAG pipelines | Flattened blocks with full HTML per chunk |

### LLM Enhancement (Requires Ollama)

When "Enable LLM Enhancement" is ON:
- Uses Ollama for accuracy improvement
- Better table extraction across pages
- Inline math to LaTeX conversion
- Form value extraction
- Requires Ollama running and model pulled

**Recommended Models**:
- `gemma2:2b` ⭐ Fast, good accuracy (~5GB)
- `llama3.2-vision` Vision-capable (~11GB)
- `llama3:8b` Higher accuracy (~4.7GB)
- `mistral:7b` Alternative option (~4.7GB)

## API Endpoints

### Backend API (Port 8000)

```
GET  /                          - Health check
GET  /health                    - Detailed system status
POST /upload                    - Upload files and start conversion
GET  /jobs                      - List all jobs
GET  /jobs/{job_id}            - Get job status
DELETE /jobs/{job_id}          - Delete job and files
GET  /download/{job_id}/{path} - Download file
GET  /preview/{job_id}/{path}  - Preview text file
```

### Example API Usage

```bash
# Upload with curl
curl -X POST http://localhost:8000/upload \
  -F "files=@document.pdf" \
  -F "use_llm=true" \
  -F "ollama_model=gemma2:2b" \
  -F "output_format=markdown"

# Check job status
curl http://localhost:8000/jobs/{job_id}

# Download result
curl http://localhost:8000/download/{job_id}/document/document.md
```

## Project Structure

```
webapp/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── uploads/            # Temporary uploaded files
│   └── outputs/            # Conversion results
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx      # Drag & drop upload
│   │   │   ├── ConfigPanel.jsx     # Settings panel
│   │   │   ├── JobList.jsx         # Job queue sidebar
│   │   │   └── ResultsViewer.jsx   # Results display
│   │   ├── App.jsx                 # Main app component
│   │   ├── main.jsx               # Entry point
│   │   └── index.css              # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

## Troubleshooting

### Backend Issues

**"marker: command not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall marker
pip install "marker-pdf[full]"

# Verify installation
which marker
marker --help
```

## API Reference

### Base URL

- Development: `http://127.0.0.1:8000`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### Endpoints

#### Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok",
  "marker_cli": true,
  "ollama": true,
  "ollama_version": "0.13.5"
}
```

#### Upload & Convert
```
POST /upload
Content-Type: multipart/form-data

Body:
  files: [file1.pdf, file2.pdf]
  use_llm: true|false
  ollama_model: "gemma2:2b"
  output_format: "markdown|json|html|chunks"
  force_ocr: true|false
```

Response:
```json
{
  "job_id": "uuid",
  "message": "Upload successful, conversion started"
}
```

#### Get Job Status
```
GET /jobs/{job_id}
```

Response:
```json
{
  "job_id": "uuid",
  "status": "pending|processing|completed|failed",
  "progress": 0-100,
  "message": "Status message",
  "files": ["output.md", "images/img1.png"],
  "error": "Error message if failed"
}
```

#### Download File
```
GET /download/{job_id}/{file_path}
```

#### Preview File
```
GET /preview/{job_id}/{file_path}
```

Response:
```json
{
  "content": "file contents",
  "filename": "output.md"
}
```

## Project Structure

```
webapp/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt     # Python deps
│   ├── uploads/            # Uploaded files
│   ├── outputs/            # Results
│   └── venv/              # Virtual env
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── FileUpload.jsx
│   │   │   ├── ConfigPanel.jsx
│   │   │   ├── JobList.jsx
│   │   │   └── ResultsViewer.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── setup.sh               # Auto setup
├── start.sh              # Start all
├── start-backend.sh      # Backend only
├── start-frontend.sh     # Frontend only
└── README.md
```

## Performance Tips

- **Backend**: Use Gunicorn with multiple workers for concurrent jobs
- **Frontend**: Lazy-load large preview content
- **Marker**: Use `--force_ocr` only for scanned documents
- **Ollama**: Keep small models cached; pull only needed models

## Known Limitations

- Job history is in-memory (lost on restart). Use a database for production.
- Large PDFs (>100MB) may timeout. Split into chunks or increase timeout.
- LLM mode requires 2GB+ free RAM per job.
- macOS: MPS acceleration requires Apple Silicon; CUDA not available.

## License

**This Web App**: MIT  
**Marker Core**: GPL-3.0-or-later + AI Pubs Open Rail-M (see [Marker repo](https://github.com/VikParuchuri/marker))

## Support & Troubleshooting

- **Marker Issues**: [GitHub Issues](https://github.com/VikParuchuri/marker/issues)
- **Ollama Support**: [Ollama GitHub](https://github.com/ollama/ollama)
- **Backend Debugging**: Check logs with `tail -f backend/uvicorn.log`
- **Health Check**: `curl -sS http://127.0.0.1:8000/health | jq`

## Changelog

### v1.0.0 (Current)
- ✅ Drag & drop file upload
- ✅ Ollama LLM integration (0.13+)
- ✅ Multi-format output
- ✅ Real-time progress tracking
- ✅ Live markdown/JSON preview
- ✅ Image gallery extraction
- ✅ Batch file download
- ✅ Responsive Tailwind design
- ✅ Python 3.11 support
- ✅ Psutil & Pydantic compatibility fixed

---

**Built with ❤️ for document intelligence**

For high-throughput production:

```bash
# In main.py, modify marker command to:
NUM_DEVICES=2 NUM_WORKERS=8 marker_chunk_convert input output
```

### Custom Processors

Modify Marker behavior by adding custom processors:

```python
# In main.py, add to marker command:
cmd.extend(["--processors", "module1.processor1,module2.processor2"])
```

### Database Integration

Replace in-memory `jobs` dict with Redis or PostgreSQL:

```python
# Install: pip install redis
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Store job
r.set(f"job:{job_id}", json.dumps(job_data))

# Retrieve job
job_data = json.loads(r.get(f"job:{job_id}"))
```

## Performance Tips

### Backend Optimization
- Use Gunicorn with multiple workers
- Implement job queue (RQ, Celery)
- Cache common conversions
- Clean up old files regularly

### Frontend Optimization
- Lazy load large result files
- Implement virtual scrolling for long documents
- Add service worker for offline support
- Compress images before display

### Marker Optimization
- Adjust `--workers` for batch processing
- Use `--force_ocr` only when needed
- Disable image extraction if not needed
- Profile conversions to find bottlenecks

## Contributing

This is a reference implementation. Feel free to:
- Add authentication and user management
- Implement persistent storage (database)
- Add more output format options
- Improve error handling
- Add unit tests
- Create Docker containers

## License

This web application wrapper is provided as-is. The underlying Marker project has its own license (GPL-3.0 + modified AI Pubs Open Rail-M for models). See the [main Marker repo](https://github.com/VikParuchuri/marker) for details.

## Support

- **Marker Issues**: https://github.com/VikParuchuri/marker/issues
- **Ollama Issues**: https://github.com/ollama/ollama/issues
- **This Web App**: Create an issue in your fork/repo

## Acknowledgments

- [Marker](https://github.com/VikParuchuri/marker) - Core document conversion engine
- [Ollama](https://ollama.com) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [React](https://react.dev) - UI library
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS
