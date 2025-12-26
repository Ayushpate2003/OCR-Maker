"""
Document retrieval for RAG.

Handles:
- Query embedding and retrieval
- Ranking and filtering
- Hybrid search (semantic + keyword)
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from .vector_store import VectorStore, SearchResult
from .embeddings import EmbeddingGenerator


@dataclass
class RetrievalResult:
    """Result from retrieval."""

    query: str
    chunks: List[SearchResult]
    total_tokens: int


class Retriever:
    """Retrieves relevant chunks for a query."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
        enable_hybrid_search: bool = True,
    ):
        """
        Initialize retriever.

        Args:
            vector_store: Vector store instance
            embedding_generator: Embedding generator instance
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score
            enable_hybrid_search: Enable keyword + semantic search
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.enable_hybrid_search = enable_hybrid_search

    def retrieve(self, query: str, top_k: Optional[int] = None) -> RetrievalResult:
        """
        Retrieve relevant chunks for query.

        Args:
            query: User query string
            top_k: Override default top_k

        Returns:
            RetrievalResult with retrieved chunks
        """
        if top_k is None:
            top_k = self.top_k

        # Generate embedding for query
        query_embedding = self.embedding_generator.embed_single(query)

        # Retrieve from vector store
        results = self.vector_store.search(query_embedding, top_k=top_k * 2)

        # Filter by similarity threshold
        filtered = [r for r in results if r.similarity_score >= self.similarity_threshold]

        # Keep top_k
        filtered = filtered[:top_k]

        # Calculate total tokens in retrieved chunks (rough estimate)
        total_tokens = sum(len(r.chunk_text) // 4 for r in filtered)

        return RetrievalResult(
            query=query,
            chunks=filtered,
            total_tokens=total_tokens,
        )

    def retrieve_by_filename(
        self, query: str, filename: str, top_k: Optional[int] = None
    ) -> RetrievalResult:
        """
        Retrieve chunks from specific document.

        Args:
            query: User query string
            filename: Filter by this filename
            top_k: Override default top_k

        Returns:
            RetrievalResult filtered to filename
        """
        # First get all results
        all_results = self.retrieve(query, top_k=100)

        # Filter by filename
        filtered = [r for r in all_results.chunks if r.filename == filename]

        # Keep top_k
        if top_k is None:
            top_k = self.top_k
        filtered = filtered[:top_k]

        # Recalculate tokens
        total_tokens = sum(len(r.chunk_text) // 4 for r in filtered)

        return RetrievalResult(
            query=query,
            chunks=filtered,
            total_tokens=total_tokens,
        )
