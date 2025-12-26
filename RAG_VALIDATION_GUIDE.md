# RAG System Validation Guide
## How to Verify Your RAG Pipeline is Working Correctly

This guide helps you validate that your Semantic RAG system is functioning properly and not hallucinating.

---

## 📋 Table of Contents

1. [Quick Start - Run Automated Tests](#quick-start)
2. [Manual Validation Steps](#manual-validation)
3. [Understanding Good vs Bad Retrieval](#retrieval-quality)
4. [Grounding Validation](#grounding-validation)
5. [Testing Methodology](#testing-methodology)
6. [Metrics & Thresholds](#metrics)
7. [Common Issues & Fixes](#troubleshooting)
8. [Expected Behaviors](#expected-behaviors)

---

## 🚀 Quick Start - Run Automated Tests {#quick-start}

### Step 1: Run the Validation Script

```bash
cd "/Volumes/Volume A/project V1/marker"
python test_rag_validation.py
```

This automated script tests:
- ✅ System health (all components running)
- ✅ Vector store status (documents indexed)
- ✅ Retrieval quality (relevant chunks found)
- ✅ LLM grounding (answers use retrieved context)
- ✅ False positive handling (admits "I don't know")
- ✅ Configuration optimization
- ✅ End-to-end sample test

**Expected Output**: Color-coded results showing pass/fail for each test.

### Step 2: Review Results

The script will show you:
- 🟢 Green = Working correctly
- 🟡 Yellow = Warning (may need adjustment)
- 🔴 Red = Issue found (needs fixing)

---

## 🔍 Manual Validation Steps {#manual-validation}

If you prefer hands-on testing or the script doesn't cover your use case:

### Test 1: Check System Health

```bash
# Check if RAG API is running
curl http://localhost:8000/api/rag/health | jq

# Expected output:
{
  "status": "healthy",
  "ollama_available": true,
  "embeddings_available": true,
  "vector_store_available": true,
  "available_models": ["gemma2:2b", "llama3:8b"]
}
```

**✅ Good**: All components show `true`
**❌ Bad**: Any component shows `false`

**Fix**: 
- Ollama not available: Run `ollama serve`
- Embeddings not available: Check sentence-transformers installation
- Vector store not available: Check ChromaDB installation

---

### Test 2: Verify Documents Are Indexed

```bash
# Check vector store statistics
curl http://localhost:8000/api/rag/stats | jq

# Expected output:
{
  "document_count": 42,
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "collection_name": "marker_documents"
}
```

**✅ Good**: `document_count > 0`
**❌ Bad**: `document_count = 0`

**Fix**: Index documents first
```bash
# Via API
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.md"}'

# Or use Web UI at http://localhost:3000
```

---

### Test 3: Test Retrieval Quality

```bash
# Query with detailed results
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "include_chunks": true
  }' | jq
```

**Look for in the response:**

```json
{
  "answer": "Machine learning is...",
  "sources": [...],
  "retrieved_chunks": [
    {
      "text": "Machine learning is a subset of artificial intelligence...",
      "similarity": 0.8234,
      "metadata": {
        "filename": "ml_guide.md",
        "heading": "Introduction to ML",
        "chunk_index": 0
      }
    }
  ]
}
```

#### Analyzing Retrieval Quality:

| Similarity Score | Quality | Meaning |
|-----------------|---------|---------|
| 0.8 - 1.0 | 🟢 Excellent | Highly relevant, semantic match |
| 0.6 - 0.8 | 🟡 Good | Relevant, useful context |
| 0.4 - 0.6 | 🟠 Acceptable | Somewhat relevant, may need tuning |
| 0.0 - 0.4 | 🔴 Poor | Irrelevant, not useful |

**✅ Good Retrieval:**
- Top chunk similarity > 0.6
- Retrieved text contains query keywords or synonyms
- Chunks are from the correct document section
- Chunks contain information needed to answer the query

**❌ Bad Retrieval:**
- All similarities < 0.4
- Retrieved text is unrelated to query
- Random chunks from irrelevant documents
- Missing obvious relevant content

---

### Test 4: LLM Grounding Test

Test if the LLM answer is based on retrieved context:

```bash
# Query without chunks (only see final answer)
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain photosynthesis",
    "top_k": 5,
    "include_chunks": false
  }' | jq
```

**✅ Good Grounded Answer:**
```
"According to the provided context, photosynthesis is the process by which 
plants convert sunlight into chemical energy. The document explains that 
chlorophyll in plant cells absorbs light energy..."

Sources:
- biology_basics.md (similarity: 0.82)
- plant_processes.md (similarity: 0.75)
```

**Indicators of good grounding:**
1. Answer references "the context" or "the document"
2. Specific details match retrieved chunks
3. Sources are cited
4. No generic knowledge outside the documents

**❌ Bad Answer (Hallucination):**
```
"Photosynthesis is a process where plants use sunlight to create food. 
It involves complex biochemical reactions including the Calvin cycle, 
light-dependent reactions, and produces glucose as the primary product..."
```

**Red flags:**
1. Too much detail not in your documents
2. Generic textbook answer
3. No source citations
4. Doesn't admit when context is insufficient

---

### Test 5: False Positive Test (Should Say "I Don't Know")

Ask a question that CANNOT be answered from your documents:

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the population of Mars colonies in 2050?",
    "top_k": 3
  }' | jq
```

**✅ Good Response (Honest):**
```
"I don't have information about Mars colonies in the provided documents. 
The context doesn't mention future population data or Mars colonization."
```

**❌ Bad Response (Hallucination):**
```
"The population of Mars colonies in 2050 is expected to be around 1 million 
people, with most living in domed cities near the equator..."
```

**This test is CRITICAL** - if your system makes up answers, it's hallucinating!

---

## 📊 Retrieval Quality - Good vs Bad {#retrieval-quality}

### Example: Good Retrieval

**Query**: "How does RAG reduce hallucinations?"

**Retrieved Chunks:**
```
Chunk 1 (similarity: 0.8456):
"Retrieval-Augmented Generation (RAG) reduces hallucinations by grounding 
LLM responses in actual documents. Instead of generating answers purely from 
training data, RAG retrieves relevant passages and uses them as context..."

Chunk 2 (similarity: 0.7892):
"The key advantage of RAG systems is that they prevent the model from 
fabricating information. By retrieving real text chunks before generation, 
the LLM is constrained to answer based on factual content..."

Chunk 3 (similarity: 0.7234):
"Hallucinations occur when language models generate plausible-sounding but 
incorrect information. RAG mitigates this by providing source documents..."
```

**Why this is good:**
✓ All chunks are highly relevant (> 0.7 similarity)
✓ Chunks discuss the exact topic (RAG + hallucinations)
✓ Information overlaps and reinforces
✓ Sufficient context to answer the question

---

### Example: Bad Retrieval

**Query**: "How does RAG reduce hallucinations?"

**Retrieved Chunks:**
```
Chunk 1 (similarity: 0.3123):
"The weather today is sunny with a high of 75 degrees..."

Chunk 2 (similarity: 0.2987):
"To install Python packages, use pip install..."

Chunk 3 (similarity: 0.2654):
"The company was founded in 1995 by John Smith..."
```

**Why this is bad:**
✗ Low similarity scores (< 0.4)
✗ Completely unrelated content
✗ No semantic connection to the query
✗ Would cause LLM to hallucinate or admit ignorance

**Root causes:**
- Documents don't contain relevant information
- Embedding model is poor quality
- Chunk size is wrong
- Documents not indexed properly

---

## 🎯 Grounding Validation {#grounding-validation}

### How to Ensure LLM Uses Retrieved Context

Your LLM prompt should be designed like this:

```python
prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided context.
If the context doesn't contain enough information to answer, say "I don't have enough information 
in the provided documents to answer this question."

Context:
{retrieved_chunks}

Question: {user_query}

Answer:"""
```

**Key elements:**
1. **Explicit instruction** to use only context
2. **Fallback phrase** when context is insufficient
3. **Context provided before question**
4. **Clear separation** between context and query

### Prompt Improvements to Prevent Hallucination

**❌ Bad Prompt (encourages hallucination):**
```
"Answer the following question: {query}"
```

**✅ Good Prompt (enforces grounding):**
```
"Based strictly on the provided context, answer the question. 
If the answer is not in the context, respond with 'The provided 
documents do not contain information about this topic.'

Context: {chunks}

Question: {query}"
```

**🌟 Best Prompt (with reasoning):**
```
"You are a document Q&A assistant. Your job is to answer questions 
using ONLY the information from the provided document excerpts below.

Rules:
1. Quote or paraphrase ONLY from the context
2. If the answer isn't in the context, say so explicitly
3. Cite which document/section your answer comes from
4. Never use outside knowledge

Context Excerpts:
{chunks}

Question: {query}

Answer (with source citations):"
```

---

## 🧪 Testing Methodology {#testing-methodology}

### A/B Testing: RAG vs No RAG

To prove RAG is working, compare answers WITH and WITHOUT retrieval:

#### Test Setup:

1. **Disable RAG** (directly query LLM):
```bash
# Query Ollama directly
curl http://localhost:11434/api/generate \
  -d '{
    "model": "gemma2:2b",
    "prompt": "What is the company's refund policy?",
    "stream": false
  }'
```

2. **Enable RAG** (query through your system):
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -d '{
    "query": "What is the company's refund policy?",
    "top_k": 5
  }'
```

#### Expected Differences:

| Aspect | Without RAG | With RAG |
|--------|------------|----------|
| **Source** | Model's training data | Your documents |
| **Accuracy** | Generic/may be wrong | Specific to your docs |
| **Citations** | None | Provides sources |
| **Admits ignorance** | Rarely | When no context found |
| **Custom info** | Cannot access | Can access |

**Example:**

**Without RAG (hallucination):**
> "Most companies offer a 30-day refund policy for unused products..."

**With RAG (grounded):**
> "According to your refund policy document, returns are accepted within 
> 14 days with a receipt. Source: company_policies.md"

---

### Fact-Based Testing

Create test questions where the answer ONLY exists in your documents:

#### Test 1: Specific Facts
```
Question: "What is the serial number of the product mentioned on page 5?"
Expected: Should retrieve exact serial number from your document
Wrong: Generic answer like "Serial numbers are typically alphanumeric..."
```

#### Test 2: Internal References
```
Question: "Who is the manager mentioned in the Q3 2024 report?"
Expected: Specific name from your document
Wrong: "Managers typically oversee teams..." (hallucination)
```

#### Test 3: Numerical Data
```
Question: "What was the revenue figure in the last quarter?"
Expected: Exact number from your financial doc
Wrong: Any estimate or generic statement
```

#### Test 4: Negative Test (Should Fail)
```
Question: "What is the password for the admin account?"
Expected: "I don't have information about passwords in these documents"
Wrong: Making up a password or security info
```

---

## 📈 Metrics & Thresholds {#metrics}

### Key Metrics to Monitor

#### 1. Similarity Scores

**What it measures:** How semantically similar retrieved chunks are to the query

**Thresholds:**
- `> 0.7` = Excellent match
- `0.5 - 0.7` = Good match
- `0.3 - 0.5` = Weak match
- `< 0.3` = Poor match (likely irrelevant)

**How to log:**
```python
for chunk in retrieved_chunks:
    print(f"Chunk similarity: {chunk['similarity']:.4f}")
    if chunk['similarity'] < 0.4:
        print("WARNING: Low similarity, may be irrelevant")
```

#### 2. Top-K Retrieval

**What it is:** Number of chunks retrieved per query

**Recommended values:**
- **Too low** (k=1-2): May miss relevant context
- **Sweet spot** (k=3-7): Balance of coverage and noise
- **Too high** (k=10+): Adds irrelevant content, slows LLM

**How to test optimal k:**
```bash
# Test with different k values
for k in 3 5 7 10; do
  curl -X POST http://localhost:8000/api/rag/query \
    -d "{\"query\": \"test\", \"top_k\": $k}" | jq '.sources | length'
done
```

#### 3. Average Similarity per Query

**Formula:**
```python
avg_similarity = sum(chunk.similarity for chunk in chunks) / len(chunks)
```

**Thresholds:**
- `> 0.6` = Query well-covered by documents
- `0.4 - 0.6` = Partially relevant documents
- `< 0.4` = Documents likely don't contain answer

#### 4. Answer Latency

**Components:**
- Embedding query: ~50-200ms
- Vector search: ~10-100ms  
- LLM generation: ~1-10s (depends on model size)

**Total acceptable:** < 15 seconds for interactive use

---

### Configuration Settings Impact

| Setting | Too Low | Optimal | Too High |
|---------|---------|---------|----------|
| **chunk_size** | Loses context | 600-1000 tokens | Adds noise |
| **chunk_overlap** | Misses info at boundaries | 100-200 tokens | Redundant content |
| **top_k** | Insufficient context | 3-7 chunks | Too much noise |
| **similarity_threshold** | Retrieves junk | 0.3-0.5 | Misses relevant chunks |
| **temperature** | Repetitive | 0.1-0.3 (RAG) | Hallucination-prone |

---

## 🐛 Common Issues & Fixes {#troubleshooting}

### Issue 1: No Chunks Retrieved

**Symptoms:**
```json
{
  "retrieved_chunks": [],
  "answer": "I don't have information about this."
}
```

**Possible causes:**
1. No documents indexed
2. Similarity threshold too high
3. Query uses different terminology than documents

**Fixes:**
```bash
# Check document count
curl http://localhost:8000/api/rag/stats | jq '.document_count'

# Lower similarity threshold
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"similarity_threshold": 0.1}'

# Try more general query
# Instead of: "What is the Q3 2024 EBITDA?"
# Try: "financial results" or "quarterly earnings"
```

---

### Issue 2: Low Similarity Scores

**Symptoms:**
All retrieved chunks have similarity < 0.4

**Possible causes:**
1. Wrong embedding model for your content
2. Poor quality documents (OCR errors, etc.)
3. Query-document vocabulary mismatch

**Fixes:**

**A) Try different embedding model:**
```bash
# Current model might be too general
# Try more specialized model
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"embedding_model": "all-mpnet-base-v2"}'

# Then re-index documents
curl -X POST http://localhost:8000/api/rag/clear
curl -X POST http://localhost:8000/api/rag/index \
  -d '{"file_path": "/path/to/docs", "clear_existing": true}'
```

**B) Improve document quality:**
```bash
# Check if Marker conversion was successful
# Re-convert with better settings if needed
```

---

### Issue 3: Wrong Chunk Size

**Symptoms:**
- Chunks too small: Missing context, incomplete sentences
- Chunks too large: Too much irrelevant info, diluted similarity

**Testing chunk size:**

```python
# Check what your chunks look like
response = requests.post(f"{BASE_URL}/query", json={
    "query": "test",
    "include_chunks": True
})

for chunk in response.json()["retrieved_chunks"]:
    print(f"Chunk length: {len(chunk['text'])} characters")
    print(f"Preview: {chunk['text'][:200]}...")
```

**Optimal chunk sizes:**
- **Short form content** (tweets, Q&A): 200-400 tokens
- **Articles, docs**: 600-1000 tokens (RECOMMENDED)
- **Technical docs**: 800-1200 tokens
- **Books, long form**: 1000-1500 tokens

**Adjust:**
```bash
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"chunk_size": 800, "chunk_overlap": 150}'

# Must re-index after changing chunk size
```

---

### Issue 4: LLM Hallucinating Despite Good Retrieval

**Symptoms:**
- Retrieved chunks are relevant (high similarity)
- But LLM answer includes information NOT in chunks

**Root cause:**
LLM is using its training data instead of the context

**Fix #1: Improve prompt**
```python
# In marker/rag/llm.py, modify the prompt:

prompt = f"""You are a Q&A assistant that MUST answer based ONLY on the provided context.

CRITICAL RULES:
1. Use ONLY information from the context below
2. Never use your general knowledge
3. If the context doesn't contain the answer, say "The provided documents do not contain this information"
4. Quote relevant parts of the context when possible

CONTEXT:
{context}

QUESTION: {query}

ANSWER (based strictly on the context above):"""
```

**Fix #2: Use more conservative temperature**
```bash
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"temperature": 0.1, "max_tokens": 500}'
```

**Fix #3: Try different LLM model**
```bash
# Some models are better at following instructions
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"llm_model": "llama3:8b"}'  # Better instruction following
```

---

### Issue 5: Retrieves Correct Chunks But Answer is Wrong

**Symptoms:**
- Chunks contain the right information
- But LLM answer is incorrect or incomplete

**Debugging steps:**

1. **Check chunk content:**
```python
# Manually read retrieved chunks
print("Retrieved chunks:")
for i, chunk in enumerate(retrieved_chunks):
    print(f"\nChunk {i+1}:")
    print(chunk['text'])

# Ask yourself: "Can I answer the question from these chunks?"
```

2. **Check prompt construction:**
```python
# In marker/rag/llm.py, add logging:
print("FULL PROMPT SENT TO LLM:")
print(prompt)
print("-" * 50)
```

3. **Test different context formatting:**
```python
# Try numbering chunks
context = "\n\n".join([
    f"[Source {i+1}]: {chunk['text']}"
    for i, chunk in enumerate(chunks)
])
```

---

### Issue 6: System Says "I Don't Know" When Answer Exists

**Symptoms:**
- You know the answer is in your documents
- But system can't find it

**Possible causes:**

1. **Document not indexed:**
```bash
# Verify document was indexed
curl http://localhost:8000/api/rag/stats
# Check document count

# Re-index if needed
curl -X POST http://localhost:8000/api/rag/index \
  -d '{"file_path": "/path/to/doc.md"}'
```

2. **Similarity threshold too high:**
```bash
# Lower threshold
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"similarity_threshold": 0.0}'

# Test query again
```

3. **Query terminology mismatch:**
```bash
# Instead of technical terms, try simpler language
# Instead of: "What is the DBMS schema structure?"
# Try: "How is the database organized?"
```

4. **Check chunk boundaries:**
```python
# Answer might be split across chunks
# Increase chunk size or overlap
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"chunk_size": 1000, "chunk_overlap": 200}'
```

---

## ✅ Expected Behaviors {#expected-behaviors}

### What Good RAG Looks Like

#### 1. Retrieved Chunk Preview

**When you query:**
```json
{
  "query": "What is machine learning?",
  "include_chunks": true
}
```

**Expected response structure:**
```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "filename": "ml_basics.md",
      "heading": "Introduction",
      "similarity": 0.8456
    }
  ],
  "retrieved_chunks": [
    {
      "text": "Machine learning is a subset of AI...",
      "similarity": 0.8456,
      "metadata": {
        "filename": "ml_basics.md",
        "heading": "Introduction",
        "chunk_index": 0,
        "page_number": 1
      }
    }
  ],
  "query_time_ms": 1245
}
```

**Verify:**
- ✅ Chunks are relevant to query
- ✅ Similarity scores > 0.5
- ✅ Sources are cited
- ✅ Answer matches chunk content

---

#### 2. Citation / Source Mapping

**Good answer with citations:**
```
"According to the employee handbook (page 12), vacation days must be 
requested at least 2 weeks in advance. The handbook also states on 
page 15 that unused vacation days roll over to the next year.

Sources:
- employee_handbook.md, Section: Vacation Policy (similarity: 0.87)
- employee_handbook.md, Section: Benefits (similarity: 0.76)"
```

**Characteristics:**
- Specific document references
- Section/heading information
- Similarity scores shown
- Clear mapping between answer parts and sources

---

#### 3. Confidence / Similarity Scoring

**High confidence (strong match):**
```json
{
  "answer": "The product costs $299",
  "confidence": "high",
  "avg_similarity": 0.89,
  "sources": [{"similarity": 0.89}, {"similarity": 0.87}]
}
```

**Medium confidence (moderate match):**
```json
{
  "answer": "The document mentions pricing but doesn't specify exact amounts",
  "confidence": "medium",
  "avg_similarity": 0.55,
  "sources": [{"similarity": 0.58}, {"similarity": 0.52}]
}
```

**Low confidence (weak match):**
```json
{
  "answer": "I don't have enough information in the provided documents to answer this question",
  "confidence": "low",
  "avg_similarity": 0.23,
  "sources": []
}
```

---

#### 4. How to Confirm Right Chunks Were Used

**Method 1: Manual inspection**
```bash
# Get query with chunks
response=$(curl -s -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question", "include_chunks": true}')

# Extract answer
echo "$response" | jq '.answer'

# Extract chunks
echo "$response" | jq '.retrieved_chunks[].text'

# Manually verify answer comes from chunks
```

**Method 2: Keyword matching**
```python
import requests

response = requests.post(f"{BASE_URL}/query", json={
    "query": "What is photosynthesis?",
    "include_chunks": True
})

answer = response.json()["answer"]
chunks = response.json()["retrieved_chunks"]

# Extract key terms from answer
answer_terms = set(answer.lower().split())

# Check if terms appear in chunks
for chunk in chunks:
    chunk_terms = set(chunk["text"].lower().split())
    overlap = answer_terms & chunk_terms
    print(f"Similarity: {chunk['similarity']:.3f}")
    print(f"Shared terms: {len(overlap)} terms")
    print(f"Sample shared terms: {list(overlap)[:10]}")
```

**Method 3: Fact checking**
```python
# For each factual claim in the answer, verify it appears in chunks

answer = "The company was founded in 1995 by John Smith"

# Check chunks contain this
assert any("1995" in chunk["text"] for chunk in chunks), "Date not in chunks!"
assert any("John Smith" in chunk["text"] for chunk in chunks), "Name not in chunks!"
```

---

## 🎯 Quick Diagnostic Queries

Test these queries to validate your system:

### Query 1: Exact Match Test
```
Query: [Use a unique phrase from your document]
Expected: High similarity (> 0.8), chunk contains exact phrase
```

### Query 2: Semantic Match Test
```
Query: [Use synonyms/paraphrase of document content]
Expected: Good similarity (> 0.6), semantically related chunks
```

### Query 3: Multi-hop Test
```
Query: "Compare X and Y"
Expected: Retrieves chunks about both X and Y
```

### Query 4: False Positive Test
```
Query: "What is [something definitely not in your docs]?"
Expected: Low similarity, LLM says "I don't know"
```

### Query 5: Ambiguous Query Test
```
Query: Single word like "process" or "system"
Expected: Multiple relevant chunks from different contexts
```

---

## 📊 Validation Checklist

Use this checklist after making changes:

### System Health
- [ ] All components healthy (health check passes)
- [ ] Documents indexed (doc count > 0)
- [ ] Ollama models available

### Retrieval Quality
- [ ] Top chunk similarity > 0.6 for known queries
- [ ] Retrieved chunks semantically related to query
- [ ] Chunks contain information needed for answer

### LLM Grounding
- [ ] Answer references "context" or "document"
- [ ] Answer cites sources
- [ ] Answer doesn't include info outside chunks
- [ ] System admits "I don't know" for unanswerable queries

### Configuration
- [ ] Chunk size: 600-1000 tokens
- [ ] Chunk overlap: 100-200 tokens
- [ ] Top-k: 3-7
- [ ] Similarity threshold: 0.3-0.5
- [ ] Temperature: 0.1-0.3

### End-to-End
- [ ] Can index a document successfully
- [ ] Can query and get relevant answers
- [ ] Citations map to correct sources
- [ ] False positive test passes (says "I don't know")

---

## 🔧 Optimization Guide

### If Retrieval is Too Broad (too many irrelevant chunks)
```bash
# Increase similarity threshold
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"similarity_threshold": 0.5}'

# Decrease top_k
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"top_k": 3}'
```

### If Retrieval is Too Narrow (missing relevant chunks)
```bash
# Decrease similarity threshold
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"similarity_threshold": 0.3}'

# Increase top_k
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"top_k": 7}'

# Increase chunk size to capture more context
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"chunk_size": 1000, "chunk_overlap": 200}'
```

### If Answers are Too Generic
```bash
# Lower temperature (more focused)
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"temperature": 0.1}'

# Use better model
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"llm_model": "llama3:8b"}'
```

### If System is Too Slow
```bash
# Use faster embedding model
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"embedding_model": "all-MiniLM-L6-v2"}'

# Use smaller LLM
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"llm_model": "gemma2:2b"}'

# Reduce top_k
curl -X PUT http://localhost:8000/api/rag/config \
  -d '{"top_k": 3, "max_tokens": 500}'
```

---

## 🎓 Understanding RAG Pipeline Flow

```
User Query: "What is machine learning?"
    ↓
[1] Embed Query → [0.123, 0.456, ..., 0.789] (384-dim vector)
    ↓
[2] Search Vector Store → Find similar chunks
    ↓
[3] Rank by Similarity:
    - Chunk A: 0.85 ← Best match
    - Chunk B: 0.78
    - Chunk C: 0.72
    ↓
[4] Retrieve Top-K (e.g., top 5)
    ↓
[5] Construct Prompt:
    "Context: [Chunk A] [Chunk B] [Chunk C]
     Question: What is machine learning?
     Answer:"
    ↓
[6] Send to LLM → Generate answer
    ↓
[7] Return:
    - Answer
    - Sources (which chunks used)
    - Similarity scores
```

**At each step, verify:**
- Step 1: Query embedding has correct dimensions
- Step 2: Search returns results (not empty)
- Step 3: Similarity scores are reasonable (> 0.3)
- Step 4: Top-K chunks are relevant
- Step 5: Prompt includes all context
- Step 6: LLM generates grounded response
- Step 7: Sources map correctly

---

## 📝 Logging for Validation

Add logging to your queries:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Log retrieval
logger.info(f"Query: {query}")
logger.info(f"Retrieved {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    logger.info(f"Chunk {i+1} similarity: {chunk['similarity']:.4f}")
    logger.info(f"Chunk {i+1} preview: {chunk['text'][:100]}...")

# Log LLM input
logger.debug(f"Prompt sent to LLM:\n{prompt}")

# Log final answer
logger.info(f"Answer: {answer}")
logger.info(f"Sources: {sources}")
```

Save logs for later analysis:
```bash
python your_rag_script.py > rag_validation.log 2>&1
```

---

## ✅ Success Criteria

Your RAG system is working correctly if:

1. ✅ **Health checks pass** - All components available
2. ✅ **Documents indexed** - Vector store has content
3. ✅ **High similarity** - Top chunks > 0.6 for known queries
4. ✅ **Relevant retrieval** - Chunks contain query-related info
5. ✅ **Grounded answers** - LLM uses retrieved context
6. ✅ **Proper citations** - Sources are provided and accurate
7. ✅ **Admits ignorance** - Says "I don't know" when appropriate
8. ✅ **No hallucinations** - Doesn't make up facts
9. ✅ **Fast response** - < 15 seconds per query
10. ✅ **Consistent behavior** - Same query → same quality answer

---

## 🚀 Next Steps

1. **Run automated validation:**
   ```bash
   python test_rag_validation.py
   ```

2. **Test with your actual documents:**
   - Index your PDFs using Marker
   - Query with domain-specific questions
   - Verify answers are accurate

3. **Iterate on configuration:**
   - Adjust chunk size based on results
   - Test different embedding models
   - Tune similarity threshold

4. **Monitor in production:**
   - Log all queries and answers
   - Track similarity scores over time
   - Collect user feedback on answer quality

5. **Read advanced guides:**
   - [RAG_GUIDE.md](RAG_GUIDE.md) - Complete system documentation
   - [API_REFERENCE.md](API_REFERENCE.md) - API details
   - [VISUAL_GUIDE.md](VISUAL_GUIDE.md) - Architecture diagrams

---

**Happy Validating!** 🎉

If you encounter issues not covered here, check the troubleshooting section in [RAG_GUIDE.md](RAG_GUIDE.md).
