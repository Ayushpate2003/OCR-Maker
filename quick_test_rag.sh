#!/bin/bash
# Quick RAG validation - Simple version

echo "🔍 Testing RAG System..."
echo ""

# Test 1: Health Check
echo "1. Health Check:"
curl -s http://localhost:8000/api/rag/health | python3 -m json.tool
echo ""

# Test 2: Stats
echo "2. Vector Store Stats:"
curl -s http://localhost:8000/api/rag/stats | python3 -m json.tool
echo ""

# Test 3: Config
echo "3. Current Configuration:"
curl -s http://localhost:8000/api/rag/config | python3 -m json.tool
echo ""

echo "✅ If you see JSON responses above, RAG is working!"
echo ""
echo "Next steps:"
echo "  1. Index a document: Use Web UI at http://localhost:3000"
echo "  2. Run full validation: python test_rag_validation.py"
echo "  3. Read guide: open RAG_VALIDATION_GUIDE.md"
