#!/usr/bin/env python3
"""
Example: Index documents using the RAG system

This script demonstrates how to index Markdown or JSON files
from Marker output into the vector database.
"""

import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from marker.rag.config import RAGConfig
    from marker.rag.indexer import RAGIndexer
except ImportError:
    print("Error: RAG modules not installed. Run: pip install -r webapp/backend/requirements-rag.txt")
    sys.exit(1)


def main():
    """
    Index example documents
    """
    # Create config
    config = RAGConfig(
        chunk_size=800,
        chunk_overlap=100,
        embedding_model="all-MiniLM-L6-v2",
        vector_db_path=Path("./data/chroma_db"),
    )

    # Create indexer
    indexer = RAGIndexer(config)

    print("🚀 RAG Indexer Example")
    print("=" * 50)
    print(f"Config: {config.to_dict()}")
    print()

    # Example 1: Index a single markdown file
    print("📄 Example 1: Index a single markdown file")
    print("-" * 50)

    markdown_content = """
# RAG System Guide

## Introduction

The Retrieval-Augmented Generation (RAG) system enables semantic search
over document collections using embeddings and a local language model.

## Key Components

### Chunking
Documents are split into overlapping semantic chunks of 800-1200 tokens.
This preserves context while maintaining reasonable retrieval speed.

### Embeddings
Text chunks are converted to 384-dimensional vectors using
sentence-transformers models. These vectors enable semantic similarity search.

### Vector Store
ChromaDB provides persistent, local storage for embeddings with
efficient similarity search using HNSW algorithm.

### LLM Integration
Ollama provides local language models (gemma2:2b, llama2:7b, etc)
for generating answers based on retrieved context.
"""

    chunks_indexed = indexer.index_markdown(
        markdown_text=markdown_content,
        filename="example.md"
    )
    print(f"✓ Indexed {chunks_indexed} chunks from example.md")
    print()

    # Example 2: Index multiple files from directory
    print("📚 Example 2: Index directory of documents")
    print("-" * 50)

    doc_dir = Path("./documents")
    if doc_dir.exists():
        results = indexer.index_directory(
            directory=doc_dir,
            pattern="*.md"
        )
        print(f"✓ Indexed {results['total_chunks']} chunks from {results['indexed_files']} files")
        if results['errors']:
            for error in results['errors']:
                print(f"  ⚠ {error}")
    else:
        print(f"ℹ Directory {doc_dir} not found. Create it with markdown files to index.")
    print()

    # Example 3: Get statistics
    print("📊 Statistics")
    print("-" * 50)
    stats = indexer.get_stats()
    print(f"Documents indexed: {stats['vector_store']['document_count']}")
    print(f"Embedding model: {stats['embedding_model']['model_name']}")
    print(f"Collection: {stats['config']['collection_name']}")
    print()

    print("✅ Indexing example complete!")
    print()
    print("Next: Use the query example to search indexed documents")


if __name__ == "__main__":
    main()
