# 🔍 Marker Semantic RAG System - Complete Guide

## Overview

The Marker Semantic RAG (Retrieval-Augmented Generation) system enables users to:

- **Convert PDFs to Markdown** using Marker CLI
- **Index converted documents** into a vector database
- **Search semantically** using natural language queries
- **Generate answers** using a local LLM with retrieved context
- **Chat with documents** through an intuitive web interface

All processing happens **locally** with no external API calls, ensuring privacy and security.

## Architecture

```
┌─────────────────┐
│   PDF Files     │
└────────┬────────┘
         │
         ├──→ Marker CLI (converts to Markdown/JSON)
         │
         ▼
┌─────────────────────────────────────────┐
│          RAG Indexing Pipeline           │
├─────────────────────────────────────────┤
│  1. Semantic Chunking (800-1200 tokens) │
│  2. Embeddings (all-MiniLM-L6-v2)       │
│  3. Vector Store (ChromaDB)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Vector Database (ChromaDB)          │
│  - Persists to ./rag_db                 │
│  - Enables semantic search              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     FastAPI Backend Endpoints            │
├─────────────────────────────────────────┤
│  POST /api/rag/index  (indexing)        │
│  POST /api/rag/query  (retrieval+LLM)   │
│  GET  /api/rag/config (settings)        │
│  GET  /api/rag/health (status)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        React Web Interface               │
├─────────────────────────────────────────┤
│  - Chat Panel (query documents)         │
│  - Settings Panel (configuration)       │
│  - Indexer Panel (upload documents)     │
└─────────────────────────────────────────┘
```

## System Requirements

### macOS

- **Python:** 3.9+
- **Node.js:** 16+ (for frontend)
- **Ollama:** Latest version (for LLM features)
- **Homebrew:** Recommended for package management
- **Disk Space:** ~2-5GB (depending on models)

### Minimum System Requirements

- **RAM:** 8GB (16GB+ recommended)
- **Storage:** 5GB free for models and vector database
- **CPU:** Apple Silicon or Intel (will work but slower on Intel)

## Installation & Setup

### 1. Quick Setup (Automated - macOS)

```bash
cd /path/to/marker
chmod +x setup_rag.sh
./setup_rag.sh
```

This script will:
- Create Python virtual environment
- Install all dependencies
- Setup Ollama (if needed)
- Configure the frontend (optional)

### 2. Manual Setup

#### 2.1 Backend Setup

```bash
cd webapp/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-rag.txt
```

#### 2.2 Install Ollama

```bash
# Using Homebrew (macOS)
brew install ollama

# Start Ollama service
brew services start ollama

# Or run manually
ollama serve
```

#### 2.3 Pull a Language Model

```bash
# Fast and lightweight (recommended for first-time)
ollama pull gemma2:2b

# Or try other models:
ollama pull llama2:7b
ollama pull llama3:8b
ollama pull qwen2.5:7b

# List available models
ollama list
```

#### 2.4 Frontend Setup (Optional)

```bash
cd webapp/frontend
npm install
```

### 3. Verify Installation

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Check Backend Health
curl http://localhost:8000/health
```

## Usage Guide

### Starting the System

#### Terminal 1: Start Ollama (if not running as service)

```bash
ollama serve
```

#### Terminal 2: Start Backend

```bash
cd webapp/backend
source venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

#### Terminal 3: Start Frontend (Optional)

```bash
cd webapp/frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173` or `http://localhost:3000`

### API Endpoints

#### Health Check

```bash
curl http://localhost:8000/api/rag/health
```

Response:
```json
{
  "rag_enabled": true,
  "embeddings_model_available": true,
  "vector_store_ready": true,
  "ollama_available": true,
  "message": "RAG system operational"
}
```

#### Index a Document

```bash
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.md",
    "clear_existing": false
  }'
```

Response:
```json
{
  "status": "success",
  "filename": "document.md",
  "chunks_created": 25,
  "message": "Successfully indexed 25 chunks from document.md"
}
```

#### Query Documents

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "top_k": 5,
    "include_chunks": false
  }'
```

Response:
```json
{
  "query": "What is the main topic?",
  "answer": "The document covers semantic search and RAG systems...",
  "sources": [
    {
      "filename": "document.md",
      "chunk_index": 0,
      "heading": "Introduction",
      "similarity_score": 0.87,
      "excerpt": "This document explores RAG systems..."
    }
  ],
  "model": "gemma2:2b",
  "tokens_used": 128,
  "confidence": 0.87
}
```

#### Get Configuration

```bash
curl http://localhost:8000/api/rag/config
```

#### Update Configuration

```bash
curl -X PUT http://localhost:8000/api/rag/config \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 1000,
    "top_k": 7,
    "ollama_model": "llama2:7b"
  }'
```

#### Get Statistics

```bash
curl http://localhost:8000/api/rag/stats
```

#### Clear Index

```bash
curl -X POST http://localhost:8000/api/rag/clear
```

### Web Interface

The React frontend provides:

#### 💬 Chat Tab
- Ask questions about indexed documents
- View retrieved sources with similarity scores
- Toggle full chunk display
- Copy answers to clipboard

#### 📚 Index Tab
- Select markdown/JSON files to index
- Clear existing index before indexing
- See indexing progress

#### ⚙️ Settings Tab
- Adjust chunk size and overlap
- Select embedding model
- Choose Ollama model
- Set top-k retrieval count
- View system statistics
- Rebuild or clear index

## Configuration Guide

### RAG Configuration (`marker/rag/config.py`)

```python
RAGConfig(
    # Enable/disable RAG
    enabled=True,
    
    # Chunking
    chunk_size=800,          # tokens per chunk
    chunk_overlap=100,       # tokens to overlap
    min_chunk_size=100,      # minimum chunk size
    
    # Embeddings
    embedding_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
    
    # Vector Store
    vector_db_path=Path("./data/chroma_db"),
    collection_name="marker_documents",
    
    # Retrieval
    top_k=5,
    similarity_threshold=0.3,
    enable_hybrid_search=True,
    
    # LLM
    ollama_base_url="http://localhost:11434",
    ollama_model="gemma2:2b",
    temperature=0.3,
    max_tokens=512,
    context_window=2048,
)
```

### Recommended Settings by Use Case

#### Fast Processing (Limited Resources)
```json
{
  "embedding_model": "all-MiniLM-L6-v2",
  "ollama_model": "gemma2:2b",
  "chunk_size": 500,
  "top_k": 3,
  "temperature": 0.3
}
```

#### Balanced (Most Systems)
```json
{
  "embedding_model": "all-MiniLM-L12-v2",
  "ollama_model": "llama2:7b",
  "chunk_size": 800,
  "top_k": 5,
  "temperature": 0.3
}
```

#### High Quality (Good Resources)
```json
{
  "embedding_model": "all-mpnet-base-v2",
  "ollama_model": "llama3:8b",
  "chunk_size": 1200,
  "top_k": 7,
  "temperature": 0.2
}
```

## Module Reference

### Core Modules

#### `marker/rag/config.py`
Manages RAG system configuration with validation and persistence.

**Key Classes:**
- `RAGConfig`: Main configuration dataclass

#### `marker/rag/chunking.py`
Splits documents into semantic chunks with metadata preservation.

**Key Classes:**
- `SemanticChunker`: Intelligent document chunking
- `ChunkMetadata`: Metadata storage for chunks

#### `marker/rag/embeddings.py`
Generates embeddings using sentence-transformers models.

**Key Classes:**
- `EmbeddingGenerator`: Creates embeddings for text
- `EmbeddingModel`: Enum of available models

#### `marker/rag/vector_store.py`
Vector database interface with ChromaDB implementation.

**Key Classes:**
- `VectorStore`: Abstract base class
- `ChromaVectorStore`: ChromaDB implementation
- `SearchResult`: Search result dataclass

#### `marker/rag/retrieval.py`
Handles query retrieval from vector database.

**Key Classes:**
- `Retriever`: Query retrieval engine
- `RetrievalResult`: Retrieval results dataclass

#### `marker/rag/llm.py`
LLM integration with Ollama for answer generation.

**Key Classes:**
- `OllamaLLM`: Ollama integration
- `QueryResult`: Answer with sources

#### `marker/rag/indexer.py`
Main indexing pipeline coordinator.

**Key Classes:**
- `RAGIndexer`: Orchestrates indexing process

### Backend API

#### `webapp/backend/rag_routes.py`
FastAPI routes for RAG endpoints.

**Endpoints:**
- `GET /api/rag/health`: Health check
- `POST /api/rag/index`: Index document
- `POST /api/rag/query`: Query and get answer
- `GET /api/rag/config`: Get configuration
- `PUT /api/rag/config`: Update configuration
- `GET /api/rag/stats`: Get statistics
- `POST /api/rag/clear`: Clear index

### Frontend Components

#### `src/hooks/useRAGAPI.js`
Custom React hook for RAG API interactions.

#### `src/components/rag/RAGPanel.jsx`
Main RAG interface component.

#### `src/components/rag/RAGChat.jsx`
Chat interface with document querying.

#### `src/components/rag/RAGSettings.jsx`
Configuration panel with sliders and dropdowns.

#### `src/components/rag/RAGIndexer.jsx`
Document indexing interface.

## Performance Optimization

### Model Selection

| Model | Speed | Quality | RAM | Comments |
|-------|-------|---------|-----|----------|
| gemma2:2b | ⚡⚡⚡ | ⭐⭐ | 2GB | Best for limited resources |
| llama2:7b | ⚡⚡ | ⭐⭐⭐ | 5GB | Good balance |
| llama3:8b | ⚡ | ⭐⭐⭐⭐ | 8GB | Best quality |
| qwen2.5:7b | ⚡⚡ | ⭐⭐⭐ | 5GB | Multilingual support |

### Embedding Models

| Model | Dimension | Speed | Quality | Notes |
|-------|-----------|-------|---------|-------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡ | ⭐⭐⭐ | **Recommended** |
| all-MiniLM-L12-v2 | 384 | ⚡⚡ | ⭐⭐⭐ | Slightly better |
| all-mpnet-base-v2 | 768 | ⚡ | ⭐⭐⭐⭐ | Higher quality |

### Optimization Tips

1. **Chunk Size**: Larger chunks = faster processing but less precision
   - Small docs (< 10 pages): 500-700 tokens
   - Medium docs (10-100 pages): 800-1000 tokens
   - Large docs (> 100 pages): 1000-1500 tokens

2. **Top-K Results**: More results = slower but higher coverage
   - Use 3-5 for simple queries
   - Use 7-10 for complex questions

3. **Temperature**: Lower = deterministic, Higher = creative
   - 0.1-0.3: For factual QA (recommended)
   - 0.5-0.7: For creative writing
   - 0.8-1.0: For brainstorming

4. **Batch Processing**: Index multiple documents at once
   - Reduces overhead
   - More efficient embedding generation

## Troubleshooting

### Issue: "Ollama not available"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if not running
brew services start ollama
# or
ollama serve
```

### Issue: "Model not found"

```bash
# List available models
ollama list

# Pull a model
ollama pull gemma2:2b
```

### Issue: "Out of memory"

Solution:
1. Use a smaller LLM (gemma2:2b instead of llama3:8b)
2. Reduce chunk_size to 500
3. Reduce top_k to 3
4. Use smaller embedding model (all-MiniLM-L6-v2)

### Issue: "Slow indexing"

Solution:
1. Reduce embedding model quality
2. Increase batch_size in config
3. Increase max_workers for parallel processing
4. Index fewer documents per request

### Issue: "Poor answer quality"

Solution:
1. Use larger, better LLM (llama3:8b)
2. Use better embedding model (all-mpnet-base-v2)
3. Increase top_k for more context
4. Reduce temperature for consistency
5. Improve document chunking strategy

### Issue: CORS errors

Ensure backend CORS is configured for frontend origin:

```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Advanced Usage

### Using Different Embedding Models

```python
from marker.rag.embeddings import EmbeddingModel

config.embedding_model = EmbeddingModel.MULTILINGUAL_MPNET.value
```

### Batch Document Indexing

```python
from marker.rag.indexer import RAGIndexer
from marker.rag.config import RAGConfig

config = RAGConfig()
indexer = RAGIndexer(config)

# Index multiple files
results = indexer.index_directory(
    directory=Path("./documents"),
    pattern="*.md"
)
print(f"Indexed {results['total_chunks']} chunks")
```

### Custom Query Parameters

```javascript
// Frontend - Advanced querying
const response = await api.queryDocuments(
  "Your question here",
  top_k=10,          // Get more results
  includeChunks=true // See full retrieved text
);
```

### Hybrid Search (Future Enhancement)

```python
# Planned feature combining semantic + keyword search
retriever.retrieve_hybrid(
    query="search term",
    top_k=5,
    semantic_weight=0.7,
    keyword_weight=0.3
)
```

## Security Considerations

### Local-Only Processing
- ✅ All processing happens locally
- ✅ No data sent to external APIs
- ✅ Complete privacy control

### Access Control (Recommended)

For production, add authentication:

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/rag/query")
async def query_documents(request: QueryRequest, credentials: HTTPAuthCredentials = Depends(security)):
    # Verify token here
    pass
```

### Rate Limiting (Recommended)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/rag/query")
@limiter.limit("10/minute")
async def query_documents(request: QueryRequest):
    pass
```

## File Structure

```
marker/
├── marker/rag/
│   ├── __init__.py
│   ├── config.py           # Configuration
│   ├── chunking.py         # Semantic chunking
│   ├── embeddings.py       # Embedding generation
│   ├── vector_store.py     # Vector DB interface
│   ├── retrieval.py        # Query retrieval
│   ├── llm.py              # LLM integration
│   └── indexer.py          # Indexing pipeline
│
├── webapp/
│   ├── backend/
│   │   ├── main.py         # FastAPI app
│   │   ├── rag_routes.py   # RAG API endpoints
│   │   └── requirements-rag.txt
│   │
│   └── frontend/
│       └── src/
│           ├── components/rag/
│           │   ├── RAGPanel.jsx
│           │   ├── RAGChat.jsx
│           │   ├── RAGSettings.jsx
│           │   ├── RAGIndexer.jsx
│           │   ├── RAGPanel.css
│           │   ├── RAGChat.css
│           │   ├── RAGSettings.css
│           │   └── RAGIndexer.css
│           │
│           └── hooks/
│               └── useRAGAPI.js
│
└── setup_rag.sh            # Setup script
```

## Data Storage

### Vector Database Location

```
./rag_db/
├── 0/
│   └── [vectorized chunk data]
├── 1/
│   └── [vectorized chunk data]
└── [ChromaDB metadata files]
```

### Clearing Data

To reset the system:

```bash
# Via API
curl -X POST http://localhost:8000/api/rag/clear

# Or manually
rm -rf ./rag_db
```

## Performance Metrics

### Indexing Performance
- ~100-500 tokens/sec (embedding generation)
- ~1000-5000 tokens/sec (chunking)
- Depends on model and hardware

### Query Performance
- Retrieval: 100-500ms
- LLM Response: 5-30 seconds (depends on model and response length)
- Total: 5-31 seconds per query

### Storage Usage
- ChromaDB: ~1-2KB per chunk
- Models: 2-8GB each
- For 1000 chunks: ~2-3MB vector storage

## Next Steps & Future Features

### Current Features
✅ Semantic chunking
✅ Multi-model embedding support
✅ Local vector storage with ChromaDB
✅ Ollama LLM integration
✅ FastAPI backend
✅ React web interface
✅ Settings panel
✅ Citation tracking

### Planned Features
🔄 Hybrid search (semantic + keyword)
🔄 Multi-document chat context
🔄 User authentication and rate limiting
🔄 Advanced analytics and logging
🔄 PDF metadata preservation
🔄 Batch document upload
🔄 Export conversation history
🔄 Document versioning

## Support & Resources

### Documentation Links
- [ChromaDB Docs](https://docs.trychroma.com)
- [Sentence Transformers](https://www.sbert.net)
- [Ollama Models](https://ollama.ai)
- [FastAPI Docs](https://fastapi.tiangolo.com)

### Getting Help
1. Check troubleshooting section above
2. Review API logs: `tail -f uvicorn.log`
3. Test endpoints with curl examples
4. Check FastAPI interactive docs: http://localhost:8000/docs

## License

Same as Marker project

## Contributing

Contributions welcome! Areas for improvement:
- Additional embedding models
- Hybrid search implementation
- Frontend enhancements
- Performance optimizations
- Documentation improvements

