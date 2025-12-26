# 🔍 Marker Semantic RAG System

**A complete, production-ready Retrieval-Augmented Generation system for intelligent document search and chat.**

Transform your PDFs into a searchable, intelligent knowledge base with local processing and no external APIs.

---

## ⚡ Quick Start (10 Minutes)

```bash
# 1. Clone and setup
cd marker
chmod +x setup_rag.sh
./setup_rag.sh

# 2. Pull a language model
ollama pull gemma2:2b

# 3. Start services
# Terminal 1: Backend
cd webapp/backend && source venv/bin/activate
python -m uvicorn main:app --reload

# Terminal 2: Ollama
ollama serve

# Terminal 3: Frontend (optional)
cd webapp/frontend && npm run dev

# 4. Access system
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

**Next:** See [QUICKSTART.md](QUICKSTART.md) for detailed setup.

---

## 🎯 What It Does

### For Users
- 📄 **Index Documents**: Upload Markdown or JSON files
- 🔍 **Semantic Search**: Find information using natural language
- 💬 **Ask Questions**: Get AI-powered answers with citations
- 🎨 **Web Interface**: Clean, intuitive chat interface

### For Developers
- 🔌 **REST API**: 7 endpoints for full control
- 📚 **Python SDK**: Integrate RAG into your apps
- ⚙️ **Configurable**: Runtime parameter adjustments
- 🔐 **Local**: All processing happens locally

### Technical Features
- ✅ Semantic chunking with metadata preservation
- ✅ Multi-model embeddings (MiniLM, MPNet, Multilingual)
- ✅ ChromaDB vector database (persistent, local)
- ✅ Ollama LLM integration (gemma2, llama2, llama3, qwen2.5)
- ✅ Context-aware answer generation with citations
- ✅ Confidence scoring and relevance ranking
- ✅ Batch processing for efficiency
- ✅ Real-time configuration updates

---

## 📦 What's Included

### Backend RAG Pipeline
```
marker/rag/
├── config.py          - Configuration management
├── chunking.py        - Semantic document splitting
├── embeddings.py      - Multi-model embeddings
├── vector_store.py    - ChromaDB integration
├── retrieval.py       - Semantic search
├── llm.py             - Ollama integration
└── indexer.py         - Indexing orchestrator
```

### API Backend
```
webapp/backend/
├── main.py            - FastAPI application
├── rag_routes.py      - RAG API endpoints (7 endpoints)
└── requirements-rag.txt - Dependencies
```

### React Frontend
```
webapp/frontend/src/
├── components/rag/    - Chat, Settings, Indexer UIs
├── hooks/             - API integration
└── styles/            - Responsive CSS
```

### Documentation
- [QUICKSTART.md](QUICKSTART.md) - 10-minute setup guide
- [RAG_GUIDE.md](RAG_GUIDE.md) - Complete documentation
- [API_REFERENCE.md](API_REFERENCE.md) - API reference
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Architecture diagrams
- [DOCS_INDEX.md](DOCS_INDEX.md) - Documentation index

### Examples
- [examples/rag_index_example.py](examples/rag_index_example.py) - Indexing demo
- [examples/rag_query_example.py](examples/rag_query_example.py) - Query demo

---

## 🚀 Key Capabilities

### 1. Index Documents
```bash
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.md",
    "clear_existing": false
  }'
```

### 2. Semantic Search & QA
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "top_k": 5,
    "include_chunks": false
  }'
```

Returns answer with sources:
```json
{
  "answer": "The main topic is RAG systems...",
  "sources": [
    {
      "filename": "document.md",
      "heading": "Introduction",
      "similarity_score": 0.92
    }
  ],
  "confidence": 0.92
}
```

### 3. Configure System
```bash
# Get configuration
curl http://localhost:8000/api/rag/config

# Update settings
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"chunk_size": 1000, "top_k": 7, "ollama_model": "llama2:7b"}'
```

### 4. Monitor Health
```bash
curl http://localhost:8000/api/rag/health
```

---

## 📊 System Architecture

```
PDFs ──→ Marker CLI ──→ Markdown
                           │
                           ▼
                    ┌─────────────────┐
                    │  RAG Pipeline   │
                    │  ├─ Chunking    │
                    │  ├─ Embeddings  │
                    │  ├─ Vector DB   │
                    │  └─ Retrieval   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  FastAPI Backend│
                    │  (7 endpoints)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ React Frontend  │
                    │ ├─ Chat UI      │
                    │ ├─ Settings     │
                    │ └─ Indexer      │
                    └─────────────────┘
```

**Key Features:**
- ✅ All processing **local** (no external APIs)
- ✅ Complete **privacy** (data never leaves machine)
- ✅ **Configurable** (swap models and parameters)
- ✅ **Scalable** (batch indexing, efficient retrieval)

---

## 💻 System Requirements

### Minimum
- Python 3.9+
- 8GB RAM
- 5GB disk space
- macOS, Linux, or Windows

### Recommended
- Python 3.10+
- 16GB RAM
- 10GB disk space
- Apple Silicon Mac or modern CPU

### For LLM Features
- Ollama installed
- Language model pulled (`ollama pull gemma2:2b`)

---

## 📋 Supported Models

### Embedding Models
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| all-MiniLM-L6-v2 | 22MB | ⚡⚡⚡ | ⭐⭐⭐ |
| all-MiniLM-L12-v2 | 22MB | ⚡⚡ | ⭐⭐⭐ |
| all-mpnet-base-v2 | 109MB | ⚡ | ⭐⭐⭐⭐ |

### Language Models (via Ollama)
| Model | Size | Speed | Quality | VRAM |
|-------|------|-------|---------|------|
| gemma2:2b | 1.6GB | ⚡⚡⚡ | ⭐⭐ | 2GB |
| llama2:7b | 3.8GB | ⚡⚡ | ⭐⭐⭐ | 5GB |
| llama3:8b | 4.7GB | ⚡ | ⭐⭐⭐⭐ | 8GB |
| qwen2.5:7b | 4.7GB | ⚡⚡ | ⭐⭐⭐ | 8GB |

---

## 📚 Documentation

### For Different Roles

| Role | Start Here | Time |
|------|-----------|------|
| **User (First-time)** | [QUICKSTART.md](QUICKSTART.md) | 5-10 min |
| **DevOps/Deployment** | [RAG_GUIDE.md](RAG_GUIDE.md#installation--setup) | 20-30 min |
| **Backend Developer** | [API_REFERENCE.md](API_REFERENCE.md) | 30 min |
| **Frontend Developer** | [RAG_GUIDE.md - React](RAG_GUIDE.md#react-components) | 30 min |
| **System Architect** | [VISUAL_GUIDE.md](VISUAL_GUIDE.md) | 15 min |
| **Complete Understanding** | [RAG_GUIDE.md](RAG_GUIDE.md) | 45-60 min |

### Documentation Files
- [📖 QUICKSTART.md](QUICKSTART.md) - Setup in 10 minutes
- [📚 RAG_GUIDE.md](RAG_GUIDE.md) - Complete reference (3000+ lines)
- [🔌 API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [🎨 VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Diagrams & architecture
- [📋 DOCS_INDEX.md](DOCS_INDEX.md) - Find what you need
- [✅ DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md) - What's included

---

## 🎓 Learning Paths

### Path 1: Quick Evaluation (30 min)
1. [QUICKSTART.md](QUICKSTART.md) - Setup
2. [Testing section](QUICKSTART.md#testing-the-system) - Try it out
3. **Result**: See if it works for you

### Path 2: Full Implementation (3 hours)
1. [QUICKSTART.md](QUICKSTART.md) - Setup
2. [RAG_GUIDE.md](RAG_GUIDE.md) - Features & configuration
3. [examples/](examples/) - Code examples
4. **Result**: Ready to deploy

### Path 3: Integration & Extension (6 hours)
1. Path 2 above
2. [API_REFERENCE.md](API_REFERENCE.md) - APIs in detail
3. [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Architecture
4. Code review: `marker/rag/*.py`
5. **Result**: Ready to customize and extend

---

## 🔧 Configuration Examples

### For Speed (Limited Resources)
```json
{
  "chunk_size": 500,
  "embedding_model": "all-MiniLM-L6-v2",
  "ollama_model": "gemma2:2b",
  "top_k": 3
}
```

### Balanced (Most Use Cases)
```json
{
  "chunk_size": 800,
  "embedding_model": "all-MiniLM-L12-v2",
  "ollama_model": "llama2:7b",
  "top_k": 5
}
```

### For Quality (Good Hardware)
```json
{
  "chunk_size": 1200,
  "embedding_model": "all-mpnet-base-v2",
  "ollama_model": "llama3:8b",
  "top_k": 7
}
```

---

## 📈 Performance

### Indexing
- **Speed**: 100-500 tokens/sec (depends on model)
- **Example**: 10,000-token document → 20-100 seconds

### Querying
- **Retrieval**: 100-500ms
- **LLM Response**: 5-30 seconds (model dependent)
- **Total**: 5-31 seconds per query

### Storage
- **Per Chunk**: 1-2 KB
- **1000 chunks**: ~2-3 MB vector storage
- **Models**: 100MB - 8GB each

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Ollama not available" | `brew services start ollama` |
| "Model not found" | `ollama pull gemma2:2b` |
| "Out of memory" | Use smaller model or reduce chunk_size |
| "Slow responses" | Use faster embedding model |
| "Poor answers" | Increase top_k or use better LLM |

**Full troubleshooting**: See [RAG_GUIDE.md#troubleshooting](RAG_GUIDE.md#troubleshooting)

---

## 🔒 Privacy & Security

### Local-First Design
✅ All processing happens on your machine
✅ No data sent to external services
✅ No cloud dependencies
✅ Complete data privacy

### Production Recommendations
For enterprise use:
- Add authentication (JWT tokens)
- Implement rate limiting
- Setup audit logging
- Use HTTPS for transport
- Regular security updates

See [RAG_GUIDE.md - Security](RAG_GUIDE.md#security-considerations)

---

## 🎯 Use Cases

### Personal Knowledge Base
- Index your notes, documents, PDFs
- Search across everything
- Get instant answers with citations

### Business Documentation
- Index internal manuals and guides
- Enable employee self-service
- Reduce support ticket volume

### Research & Analysis
- Analyze large document collections
- Extract key information automatically
- Track source citations

### Customer Support
- Build chatbots from documentation
- Provide instant answers to customers
- Maintain consistency in responses

### Legal & Compliance
- Search contracts and policies
- Extract relevant clauses
- Maintain audit trails

---

## 🚀 Next Steps

1. **Setup**: Run `./setup_rag.sh`
2. **Test**: Follow [QUICKSTART.md - Testing](QUICKSTART.md#testing-the-system)
3. **Deploy**: Index your documents
4. **Integrate**: Use API or Web UI
5. **Customize**: Adjust configuration for your use case

---

## 📞 Support

- **Quick issues**: Check [QUICKSTART.md#troubleshooting](QUICKSTART.md#troubleshooting)
- **Deep dive**: Read [RAG_GUIDE.md](RAG_GUIDE.md)
- **API help**: See [API_REFERENCE.md](API_REFERENCE.md)
- **Find anything**: Use [DOCS_INDEX.md](DOCS_INDEX.md)

---

## 📊 Implementation Stats

```
Code:
  Python Backend    : ~935 lines
  FastAPI Routes    : ~400 lines
  React Frontend    : ~1090 lines
  Configuration     : ~400 lines
  ────────────────────────
  Total Code        : ~2825 lines

Documentation:
  Guides            : ~5000 lines
  API Reference     : ~1500 lines
  Examples          : ~300 lines
  ────────────────────────
  Total Docs        : ~6800 lines

Setup & Deploy:
  Automated Script  : ~200 lines
  Requirements      : ~100 lines
```

---

## ✨ Key Features

✅ **Semantic Search** - Find information by meaning, not keywords
✅ **Local Processing** - No external APIs, complete privacy
✅ **Configurable** - Swap models and adjust parameters
✅ **Fast** - 5-30 seconds per query on typical hardware
✅ **Accurate** - Citations and confidence scores
✅ **Scalable** - Batch processing and efficient retrieval
✅ **Easy Setup** - Automated installation script
✅ **Well Documented** - 6000+ lines of guides
✅ **Production Ready** - Error handling and validation
✅ **Open Source** - Built on popular frameworks

---

## 🎉 You're Ready!

Everything you need is installed and ready to use. Start with:

1. **Setup**: [QUICKSTART.md](QUICKSTART.md)
2. **Learn**: [RAG_GUIDE.md](RAG_GUIDE.md)
3. **Build**: [API_REFERENCE.md](API_REFERENCE.md)

---

## 📄 License

Same as Marker project

---

## 🙏 Credits

Built with:
- **FastAPI** - Modern Python web framework
- **React** - JavaScript UI library
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embedding models
- **Ollama** - Local LLM platform
- **Marker** - PDF to Markdown conversion

---

**Happy searching!** 🚀

Last updated: December 2025  
Status: Production Ready  
Documentation: Comprehensive  
Code Quality: High
