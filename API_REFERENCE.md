# 🔌 Marker RAG - Complete API Reference

## Base URL

```
http://localhost:8000/api/rag
```

## Authentication

Currently no authentication required. For production, add JWT or API key authentication.

## Response Format

All responses are JSON. Errors return appropriate HTTP status codes with error details.

### Success Response Format

```json
{
  "status": "success",
  "data": {...}
}
```

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

### 1. Health Check

Check if RAG system is operational and all components are available.

**Endpoint:**
```
GET /health
```

**Parameters:** None

**Response:**
```json
{
  "rag_enabled": true,
  "embeddings_model_available": true,
  "vector_store_ready": true,
  "ollama_available": true,
  "message": "RAG system operational"
}
```

**Status Codes:**
- `200`: System healthy
- `500`: Internal error

**Example:**
```bash
curl http://localhost:8000/api/rag/health
```

---

### 2. Index Document

Index a Markdown or JSON file for semantic search.

**Endpoint:**
```
POST /index
```

**Request Body:**
```json
{
  "file_path": "/path/to/document.md",
  "clear_existing": false
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | Full path to markdown or JSON file |
| clear_existing | boolean | No | Clear index before indexing (default: false) |

**Response:**
```json
{
  "status": "success",
  "filename": "document.md",
  "chunks_created": 25,
  "message": "Successfully indexed 25 chunks from document.md"
}
```

**Status Codes:**
- `200`: Document indexed successfully
- `400`: Invalid request
- `404`: File not found
- `500`: Indexing error

**Examples:**

Index with clearing existing:
```bash
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/doc.md",
    "clear_existing": true
  }'
```

Index JSON:
```bash
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/output.json",
    "clear_existing": false
  }'
```

---

### 3. Query Documents

Query indexed documents and get AI-generated answers with sources.

**Endpoint:**
```
POST /query
```

**Request Body:**
```json
{
  "query": "What is the main topic?",
  "top_k": 5,
  "include_chunks": false
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | string | Yes | User question or search query |
| top_k | integer | No | Number of chunks to retrieve (default: 5, max: 20) |
| include_chunks | boolean | No | Include full retrieved chunks in response (default: false) |

**Response:**
```json
{
  "query": "What is the main topic?",
  "answer": "The document primarily discusses semantic search and RAG systems...",
  "sources": [
    {
      "filename": "document.md",
      "chunk_index": 0,
      "heading": "Introduction",
      "similarity_score": 0.87,
      "excerpt": "This document explores RAG systems..."
    },
    {
      "filename": "document.md",
      "chunk_index": 2,
      "heading": "Overview",
      "similarity_score": 0.82,
      "excerpt": "RAG enables AI models to access..."
    }
  ],
  "model": "gemma2:2b",
  "tokens_used": 128,
  "confidence": 0.87,
  "retrieved_chunks": null
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| query | string | The original query |
| answer | string | AI-generated answer |
| sources | array | List of retrieved sources with citations |
| model | string | LLM model used |
| tokens_used | integer | Tokens generated in response |
| confidence | number | Confidence score (0-1) based on retrieval quality |
| retrieved_chunks | array | Full chunks if include_chunks=true |

**Status Codes:**
- `200`: Query successful
- `400`: Invalid query or empty query
- `500`: Query processing error

**Examples:**

Simple query:
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does RAG work?",
    "top_k": 5
  }'
```

Query with full chunks:
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits?",
    "top_k": 3,
    "include_chunks": true
  }'
```

---

### 4. Get Configuration

Retrieve current RAG system configuration.

**Endpoint:**
```
GET /config
```

**Parameters:** None

**Response:**
```json
{
  "enabled": true,
  "chunk_size": 800,
  "chunk_overlap": 100,
  "embedding_model": "all-MiniLM-L6-v2",
  "ollama_model": "gemma2:2b",
  "top_k": 5,
  "vector_db_path": "/path/to/rag_db",
  "collection_name": "marker_documents",
  "similarity_threshold": 0.3,
  "temperature": 0.3,
  "max_tokens": 512
}
```

**Status Codes:**
- `200`: Configuration retrieved
- `500`: Error retrieving configuration

**Example:**
```bash
curl http://localhost:8000/api/rag/config
```

---

### 5. Update Configuration

Modify RAG system configuration. Changes take effect immediately.

**Endpoint:**
```
PUT /config
```

**Request Body:**
```json
{
  "chunk_size": 1000,
  "top_k": 7,
  "ollama_model": "llama2:7b",
  "temperature": 0.2
}
```

**Parameters:**
| Name | Type | Modifiable | Description |
|------|------|-----------|-------------|
| chunk_size | integer | ✓ | Tokens per chunk (200-2000) |
| chunk_overlap | integer | ✓ | Overlap between chunks (0-500) |
| top_k | integer | ✓ | Results to retrieve (1-10) |
| similarity_threshold | number | ✓ | Min similarity (0-1) |
| temperature | number | ✓ | LLM temperature (0-1) |
| max_tokens | integer | ✓ | Max response tokens (128-2048) |
| ollama_model | string | ✓ | LLM model name |
| embedding_model | string | ✗ | Cannot change without re-indexing |
| vector_db_path | string | ✗ | Cannot change runtime |

**Response:**
Returns updated configuration (same as GET /config)

**Status Codes:**
- `200`: Configuration updated
- `400`: Invalid parameter value
- `500`: Update error

**Examples:**

Update multiple settings:
```bash
curl -X PUT http://localhost:8000/api/rag/config \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 1000,
    "top_k": 7,
    "temperature": 0.2,
    "ollama_model": "llama2:7b"
  }'
```

Adjust quality vs speed:
```bash
# For speed
curl -X PUT http://localhost:8000/api/rag/config \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 500,
    "top_k": 3,
    "temperature": 0.3
  }'

# For quality
curl -X PUT http://localhost:8000/api/rag/config \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 1200,
    "top_k": 7,
    "temperature": 0.2
  }'
```

---

### 6. Get Statistics

Get information about indexed documents and system status.

**Endpoint:**
```
GET /stats
```

**Parameters:** None

**Response:**
```json
{
  "vector_store": {
    "collection_name": "marker_documents",
    "document_count": 125,
    "db_path": "/path/to/rag_db"
  },
  "embedding_model": {
    "model_name": "all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "device": "cpu"
  },
  "config": {
    "enabled": true,
    "chunk_size": 800,
    "chunk_overlap": 100,
    ...
  }
}
```

**Status Codes:**
- `200`: Statistics retrieved
- `500`: Error retrieving statistics

**Example:**
```bash
curl http://localhost:8000/api/rag/stats
```

---

### 7. Clear Index

Delete all indexed documents and reset the vector database.

**Endpoint:**
```
POST /clear
```

**Request Body:** None

**Response:**
```json
{
  "status": "success",
  "message": "Index cleared"
}
```

**Status Codes:**
- `200`: Index cleared successfully
- `500`: Error clearing index

**⚠️ Warning:** This operation is irreversible. All indexed documents will be deleted.

**Example:**
```bash
curl -X POST http://localhost:8000/api/rag/clear
```

---

## Data Types

### ChunkMetadata

```typescript
{
  filename: string;        // Source file name
  chunk_index: number;     // Position in document
  heading?: string;        // Section heading if present
  section?: string;        // Section name
  page_number?: number;    // Page number (if available)
  total_chunks?: number;   // Total chunks in document
}
```

### RetrievedChunk

```typescript
{
  chunk_text: string;      // The actual text content
  similarity_score: number;  // 0-1, higher = more relevant
  metadata: ChunkMetadata; // Chunk metadata
  chunk_index: number;     // Position in document
  filename: string;        // Source filename
}
```

### Source

```typescript
{
  filename: string;        // Source document
  chunk_index: number;     // Chunk position
  heading?: string;        // Section heading
  similarity_score: number;  // Relevance score
  excerpt: string;         // First 200 chars of chunk
}
```

---

## Error Responses

### 400 Bad Request

Invalid request parameters:
```json
{
  "detail": "Query cannot be empty"
}
```

### 404 Not Found

Resource not found:
```json
{
  "detail": "File not found: /path/to/file.md"
}
```

### 500 Internal Server Error

Server-side error:
```json
{
  "detail": "Ollama not available at http://localhost:11434 or model 'gemma2:2b' not found"
}
```

---

## Rate Limiting & Timeouts

| Operation | Timeout | Notes |
|-----------|---------|-------|
| Index | 5 minutes | Longer for large files |
| Query | 2 minutes | LLM response can be slow |
| Health check | 5 seconds | Quick check |
| Config get | 1 second | No processing |

---

## Best Practices

### 1. Error Handling

Always check response status and error details:

```bash
response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}')

status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$status" != "200" ]; then
  echo "Error: $body"
fi
```

### 2. Handling Large Queries

For large documents, break into smaller indexed chunks:

```bash
# Index in batches
curl -X POST http://localhost:8000/api/rag/index \
  -d '{"file_path": "doc1.md", "clear_existing": true}'

curl -X POST http://localhost:8000/api/rag/index \
  -d '{"file_path": "doc2.md", "clear_existing": false}'
```

### 3. Monitoring Performance

Check stats before and after indexing:

```bash
# Before
curl http://localhost:8000/api/rag/stats | jq '.vector_store.document_count'

# Index
curl -X POST http://localhost:8000/api/rag/index \
  -d '{"file_path": "document.md"}'

# After
curl http://localhost:8000/api/rag/stats | jq '.vector_store.document_count'
```

### 4. Testing Queries

Test with simple queries first:

```bash
# Simple
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "main topic", "top_k": 3}'

# Then more complex
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does X relate to Y?", "top_k": 5, "include_chunks": true}'
```

---

## Integration Examples

### Python Client

```python
import requests

API_BASE = "http://localhost:8000/api/rag"

# Health check
response = requests.get(f"{API_BASE}/health")
print(response.json())

# Query
response = requests.post(
    f"{API_BASE}/query",
    json={
        "query": "What is RAG?",
        "top_k": 5
    }
)
result = response.json()
print(result["answer"])
```

### JavaScript/Node.js

```javascript
const API_BASE = "http://localhost:8000/api/rag";

// Health check
const health = await fetch(`${API_BASE}/health`).then(r => r.json());
console.log(health);

// Query
const response = await fetch(`${API_BASE}/query`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "What is RAG?",
    top_k: 5
  })
});
const result = await response.json();
console.log(result.answer);
```

### cURL Shell Script

```bash
#!/bin/bash

API="http://localhost:8000/api/rag"

# Function to query
query_rag() {
  local question=$1
  curl -s -X POST "$API/query" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$question\", \"top_k\": 5}"
}

# Usage
result=$(query_rag "What is the main topic?")
echo "$result" | jq '.answer'
```

---

## Performance Benchmarks

Typical performance on Apple Silicon Mac (M1/M2):

| Operation | Time | Notes |
|-----------|------|-------|
| Index 100 chunks | 5-10s | Embedding generation |
| Simple query | 3-8s | Retrieval + LLM response |
| Complex query | 10-30s | Longer LLM response |
| Health check | <1s | No processing |

---

## Troubleshooting API Issues

### Request Timeout

**Problem**: Query takes too long
**Solution**:
```bash
# Use smaller model
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"ollama_model": "gemma2:2b", "max_tokens": 256}'
```

### "Model not found"

**Problem**: Ollama model not available
**Solution**:
```bash
# Pull the model
ollama pull gemma2:2b

# Verify
ollama list
```

### CORS Errors

**Problem**: Frontend can't reach API
**Solution**: Ensure backend CORS is configured for frontend origin

### Empty Responses

**Problem**: No sources retrieved
**Solution**:
```bash
# Lower similarity threshold
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"similarity_threshold": 0.2}'

# Or increase top_k
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"top_k": 10}'
```

---

## API Versioning

Current version: `1.0`

Future versions will maintain backward compatibility.

---

## Support

For issues or feature requests, refer to the main documentation in `RAG_GUIDE.md` and `QUICKSTART.md`.
