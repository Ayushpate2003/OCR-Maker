"""
Marker Web Application Backend
FastAPI server that handles file uploads and runs Marker conversion jobs
"""
import os
import sys
import uuid
import shutil
import subprocess
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import json

# Add marker root to path
MARKER_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(MARKER_ROOT))

# Import RAG module
try:
    from marker.rag.config import RAGConfig
    from rag_routes import create_rag_router
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"Warning: RAG module not available: {e}")
    print("Install dependencies: pip install chromadb sentence-transformers")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Marker Conversion API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize RAG if available
if RAG_AVAILABLE:
    try:
        rag_config = RAGConfig(
            enabled=True,
            vector_db_path=BASE_DIR / "rag_db",
            ollama_base_url="http://localhost:11434",
        )
        rag_router = create_rag_router(rag_config)
        app.include_router(rag_router)
        logger.info("RAG system initialized and integrated")
    except Exception as e:
        logger.warning(f"Could not initialize RAG system: {str(e)}")
        RAG_AVAILABLE = False

# In-memory job storage (use Redis/DB for production)
jobs = {}


class ConversionRequest(BaseModel):
    use_llm: bool = False
    ollama_model: str = "gemma2:2b"
    output_format: str = "markdown"
    force_ocr: bool = False


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int
    message: str
    files: List[str] = []
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    # Remove path separators and dangerous characters
    safe_name = os.path.basename(filename)
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._- ")
    return safe_name[:255]  # Limit length


def run_marker_command(job_id: str, input_dir: Path, output_dir: Path, config: ConversionRequest):
    """Run Marker CLI command in subprocess"""
    try:
        # Update job status
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Starting conversion..."

        # Get marker command path (use venv marker if available)
        marker_cmd = "/Volumes/Volume A/project V1/marker/venv/bin/marker"
        if not os.path.exists(marker_cmd):
            marker_cmd = "marker"  # fallback to PATH

        # Build marker command
        cmd = [
            marker_cmd,
            str(input_dir),
            "--output_dir", str(output_dir)
        ]

        # Add output format
        if config.output_format == "json":
            cmd.extend(["--output_format", "json"])
        elif config.output_format == "html":
            cmd.extend(["--output_format", "html"])
        elif config.output_format == "chunks":
            cmd.extend(["--output_format", "chunks"])
        # markdown is default

        # Add LLM options
        if config.use_llm:
            cmd.append("--use_llm")
            cmd.extend(["--llm_service", "marker.services.ollama.OllamaService"])
            cmd.extend(["--ollama_model", config.ollama_model])

        # Add OCR option
        if config.force_ocr:
            cmd.append("--force_ocr")

        jobs[job_id]["progress"] = 30
        jobs[job_id]["message"] = "Running Marker conversion..."

        # Run command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            # Success - collect output files
            output_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(output_dir)
                    output_files.append(str(rel_path))

            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["message"] = "Conversion completed successfully"
            jobs[job_id]["files"] = output_files
            jobs[job_id]["completed_at"] = datetime.now().isoformat()
        else:
            # Error
            error_msg = result.stderr or result.stdout or "Unknown error"
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["progress"] = 0
            jobs[job_id]["message"] = "Conversion failed"
            jobs[job_id]["error"] = error_msg
            jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = "Conversion timeout (exceeded 10 minutes)"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now().isoformat()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Marker Web API is running"}


@app.get("/health")
async def health():
    """Detailed health check"""
    # Check if marker CLI is available
    try:
        result = subprocess.run(["marker", "--help"], capture_output=True, timeout=5)
        marker_available = result.returncode == 0
    except:
        marker_available = False

    # Check if ollama API is available
    try:
        import urllib.request, json as _json
        with urllib.request.urlopen("http://localhost:11434/api/version", timeout=3) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
            ollama_available = bool(data.get("version"))
            ollama_version = data.get("version")
    except Exception:
        ollama_available = False
        ollama_version = None

    return {
        "status": "ok",
        "marker_cli": marker_available,
        "ollama": ollama_available,
        "ollama_version": ollama_version,
        "uploads_dir": str(UPLOAD_DIR),
        "outputs_dir": str(OUTPUT_DIR)
    }


@app.post("/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    use_llm: bool = Form(False),
    ollama_model: str = Form("gemma2:2b"),
    output_format: str = Form("markdown"),
    force_ocr: bool = Form(False),
):
    """
    Upload PDF files and start conversion job
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job directories
    job_upload_dir = UPLOAD_DIR / job_id
    job_output_dir = OUTPUT_DIR / job_id
    job_upload_dir.mkdir(parents=True, exist_ok=True)
    job_output_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded files
    uploaded_files = []
    try:
        for file in files:
            # Validate file type
            if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Only PDF and image files are supported."
                )

            # Sanitize filename
            safe_filename = sanitize_filename(file.filename)
            file_path = job_upload_dir / safe_filename

            # Check file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size of 100MB"
                )

            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append(safe_filename)

    except Exception as e:
        # Cleanup on error
        shutil.rmtree(job_upload_dir, ignore_errors=True)
        shutil.rmtree(job_output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Create job record
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "Files uploaded, queued for processing",
        "files": [],
        "error": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "uploaded_files": uploaded_files
    }

    # Start background conversion
    config = ConversionRequest(
        use_llm=use_llm,
        ollama_model=ollama_model,
        output_format=output_format,
        force_ocr=force_ocr
    )
    background_tasks.add_task(run_marker_command, job_id, job_upload_dir, job_output_dir, config)

    return {"job_id": job_id, "message": "Upload successful, conversion started"}


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a conversion job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.get("/jobs")
async def list_jobs():
    """List all conversion jobs"""
    return {"jobs": list(jobs.values())}


@app.get("/download/{job_id}/{file_path:path}")
async def download_file(job_id: str, file_path: str):
    """Download a specific output file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Sanitize file path
    safe_path = Path(file_path).as_posix()
    output_file = OUTPUT_DIR / job_id / safe_path
    
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Prevent path traversal
    try:
        output_file.resolve().relative_to((OUTPUT_DIR / job_id).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type="application/octet-stream"
    )


@app.get("/preview/{job_id}/{file_path:path}")
async def preview_file(job_id: str, file_path: str):
    """Preview a file (for markdown, text, JSON)"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    safe_path = Path(file_path).as_posix()
    output_file = OUTPUT_DIR / job_id / safe_path
    
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Prevent path traversal
    try:
        output_file.resolve().relative_to((OUTPUT_DIR / job_id).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read file content
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content, "filename": output_file.name}
    except:
        raise HTTPException(status_code=400, detail="Cannot preview binary file")


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete directories
    shutil.rmtree(UPLOAD_DIR / job_id, ignore_errors=True)
    shutil.rmtree(OUTPUT_DIR / job_id, ignore_errors=True)
    
    # Remove from jobs dict
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}


# Initialize RAG routes if available
if RAG_AVAILABLE:
    try:
        # Initialize RAG config
        rag_config = RAGConfig()  # Uses defaults or loads from file
        rag_router = create_rag_router(rag_config)
        app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])
        logger.info("✓ RAG endpoints enabled at /api/rag")
    except Exception as e:
        logger.warning(f"Failed to initialize RAG routes: {e}")
        RAG_AVAILABLE = False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
