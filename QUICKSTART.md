# 🚀 Marker RAG System - Quick Start Guide

This guide will get you up and running with the Semantic RAG system in 10 minutes.

## Prerequisites Check

Before starting, verify you have:

```bash
# Check Python (need 3.9+)
python3 --version

# Check Homebrew (macOS)
brew --version

# If you don't have Homebrew, install from https://brew.sh
```

## Step-by-Step Setup (macOS)

### Step 1: Run Automated Setup (2 minutes)

```bash
# Navigate to marker directory
cd /path/to/marker

# Make setup script executable
chmod +x setup_rag.sh

# Run setup
./setup_rag.sh
```

The script will automatically:
- ✓ Create Python virtual environment
- ✓ Install all dependencies
- ✓ Setup Ollama
- ✓ Configure frontend (optional)

### Step 2: Install Ollama Model (2-5 minutes)

Ollama models are large language models that run locally.

```bash
# Start Ollama (if not running)
brew services start ollama

# Pull a model (in another terminal)
# Fast option (recommended for first time):
ollama pull gemma2:2b

# Other options:
# ollama pull llama2:7b      (better quality, larger)
# ollama pull llama3:8b      (best quality, largest)

# Verify model is installed
ollama list
```

### Step 3: Start the Backend (1 terminal)

```bash
cd /path/to/marker/webapp/backend

# Activate virtual environment
source venv/bin/activate

# Start server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Start the Frontend (Optional, another terminal)

```bash
cd /path/to/marker/webapp/frontend

# Start dev server
npm run dev
```

Expected output:
```
  ➜  local:   http://localhost:5173/
```

## Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8000/api/rag/health
```

Expected response:
```json
{
  "rag_enabled": true,
  "embeddings_model_available": true,
  "vector_store_ready": true,
  "ollama_available": true,
  "message": "RAG system operational"
}
```

### Test 2: Create Sample Document

Create a file called `sample.md`:

```bash
cat > /tmp/sample.md << 'EOF'
# Understanding RAG Systems

## What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that combines 
information retrieval with language generation. It allows AI models 
to access and cite specific information from documents.

## How RAG Works

1. **Document Indexing**: Convert documents into embeddings
2. **Semantic Search**: Find relevant chunks using similarity
3. **Context Injection**: Feed retrieved text to the LLM
4. **Answer Generation**: Generate answers based on context

## Benefits

- Provides current information
- Cites specific sources
- Reduces hallucinations
- Works with any document

## Example Use Cases

- Customer support chatbots
- Research assistants
- Knowledge base Q&A
- Documentation search
EOF
```

### Test 3: Index the Document

```bash
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/tmp/sample.md",
    "clear_existing": true
  }'
```

Expected response:
```json
{
  "status": "success",
  "filename": "sample.md",
  "chunks_created": 3,
  "message": "Successfully indexed 3 chunks from sample.md"
}
```

### Test 4: Query the Document

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "top_k": 3,
    "include_chunks": false
  }'
```

Expected response:
```json
{
  "query": "What is RAG?",
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that combines...",
  "sources": [
    {
      "filename": "sample.md",
      "chunk_index": 0,
      "heading": "What is RAG?",
      "similarity_score": 0.92,
      "excerpt": "Retrieval-Augmented Generation (RAG) is a technique..."
    }
  ],
  "model": "gemma2:2b",
  "confidence": 0.92
}
```

## Using the Web Interface

1. Open http://localhost:5173 (frontend) or http://localhost:3000
2. Navigate to the RAG panel
3. Use tabs:
   - **Chat**: Ask questions about indexed documents
   - **Index**: Upload markdown/JSON files to index
   - **Settings**: Configure system behavior

## Common Tasks

### Index a Real PDF

```bash
# Convert PDF using Marker
marker /path/to/file.pdf --output_dir ./converted

# Index the converted markdown
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "./converted/file.md",
    "clear_existing": false
  }'
```

### Try Different Models

```bash
# Update config to use a better model
curl -X PUT http://localhost:8000/api/rag/config \
  -H "Content-Type: application/json" \
  -d '{
    "ollama_model": "llama2:7b",
    "chunk_size": 1000,
    "top_k": 7
  }'

# Note: First pull the model with ollama
# ollama pull llama2:7b
```

### Clear Index

```bash
curl -X POST http://localhost:8000/api/rag/clear
```

## Troubleshooting

### "Ollama not available"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not, start it
brew services start ollama

# Or run manually in another terminal
ollama serve
```

### "Model not found"

```bash
# List available models
ollama list

# Pull a model
ollama pull gemma2:2b
```

### "CORS errors"

Make sure frontend origin is in allowed_origins in `main.py`:

```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

### Slow responses

Try a faster model:
```bash
ollama pull gemma2:2b  # Fastest
# Instead of
ollama pull llama3:8b  # Slower but better
```

## Next Steps

1. ✅ Read [RAG_GUIDE.md](RAG_GUIDE.md) for complete documentation
2. ✅ Try [examples/rag_index_example.py](examples/rag_index_example.py) for Python API usage
3. ✅ Explore [examples/rag_query_example.py](examples/rag_query_example.py) for advanced queries
4. ✅ Customize settings for your use case

## File Locations

- **Backend**: `webapp/backend/`
- **Frontend**: `webapp/frontend/`
- **RAG Core**: `marker/rag/`
- **Vector DB**: `./rag_db/`
- **Configuration**: `marker/rag/config.py`
- **API Routes**: `webapp/backend/rag_routes.py`

## Key Commands Reference

```bash
# Start/stop services
brew services start ollama
brew services stop ollama

# Ollama management
ollama list              # List models
ollama pull gemma2:2b   # Download model
ollama serve            # Run manually

# Backend
cd webapp/backend
source venv/bin/activate
python -m uvicorn main:app --reload

# Frontend
cd webapp/frontend
npm run dev

# API testing
curl http://localhost:8000/api/rag/health
curl -X POST http://localhost:8000/api/rag/query -H "Content-Type: application/json" -d '{...}'

# Python examples
python examples/rag_index_example.py
python examples/rag_query_example.py
```

## Getting Help

1. **Installation Issues**: Check [RAG_GUIDE.md - Troubleshooting](RAG_GUIDE.md#troubleshooting)
2. **API Questions**: Review [RAG_GUIDE.md - API Endpoints](RAG_GUIDE.md#api-endpoints)
3. **Performance**: Check [RAG_GUIDE.md - Performance Optimization](RAG_GUIDE.md#performance-optimization)
4. **Code Examples**: Look in `examples/` directory

## Success Indicators

✅ You're ready when:
- [ ] `curl http://localhost:8000/health` returns {"status": "ok"}
- [ ] `curl http://localhost:8000/api/rag/health` shows "RAG system operational"
- [ ] You can index a document without errors
- [ ] You can query and get an answer with sources
- [ ] Web interface loads at http://localhost:5173

---

**💡 Tip**: Start with `gemma2:2b` model. It's fast and uses less RAM. You can always switch to `llama2:7b` or `llama3:8b` later for better quality.

**⚡ Performance**: First query will be slow (model loads into memory). Subsequent queries are much faster.

**🔒 Privacy**: All processing happens locally. Nothing leaves your machine.

Enjoy! 🎉
