"""
Semantic RAG (Retrieval-Augmented Generation) module for Marker.

This module provides:
- Document chunking and semantic splitting
- Embedding generation with multiple models
- Vector database storage with ChromaDB
- Query retrieval and ranking
- LLM integration for answer generation
"""

from .chunking import SemanticChunker, ChunkMetadata
from .embeddings import EmbeddingModel, EmbeddingGenerator
from .vector_store import VectorStore, ChromaVectorStore
from .retrieval import Retriever, RetrievalResult
from .llm import OllamaLLM, QueryResult

__all__ = [
    "SemanticChunker",
    "ChunkMetadata",
    "EmbeddingModel",
    "EmbeddingGenerator",
    "VectorStore",
    "ChromaVectorStore",
    "Retriever",
    "RetrievalResult",
    "OllamaLLM",
    "QueryResult",
]
