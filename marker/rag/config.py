"""
Configuration for RAG system.

Handles all RAG settings including embedding models, chunk sizes, and storage.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json


@dataclass
class RAGConfig:
    """Configuration for the RAG system."""

    # RAG enable/disable
    enabled: bool = True

    # Chunking settings
    chunk_size: int = 800  # tokens per chunk
    chunk_overlap: int = 100  # tokens overlap
    min_chunk_size: int = 100  # minimum chunk size

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"  # HuggingFace model ID
    embedding_dimension: int = 384  # dimension of embeddings

    # Vector store settings
    vector_db_path: Path = Path("./data/chroma_db")  # ChromaDB storage
    collection_name: str = "marker_documents"

    # Retrieval settings
    top_k: int = 5  # number of chunks to retrieve
    similarity_threshold: float = 0.3  # minimum similarity score
    enable_hybrid_search: bool = True  # semantic + keyword search

    # LLM settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:2b"
    context_window: int = 2048
    temperature: float = 0.3
    max_tokens: int = 512

    # Processing settings
    max_workers: int = 4  # parallel processing workers
    batch_size: int = 32  # batch size for embeddings

    def __post_init__(self):
        """Ensure paths are Path objects."""
        if isinstance(self.vector_db_path, str):
            self.vector_db_path = Path(self.vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        """Convert config to dictionary (for JSON serialization)."""
        return {
            "enabled": self.enabled,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "min_chunk_size": self.min_chunk_size,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "vector_db_path": str(self.vector_db_path),
            "collection_name": self.collection_name,
            "top_k": self.top_k,
            "similarity_threshold": self.similarity_threshold,
            "enable_hybrid_search": self.enable_hybrid_search,
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "context_window": self.context_window,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_workers": self.max_workers,
            "batch_size": self.batch_size,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RAGConfig":
        """Create config from dictionary."""
        if "vector_db_path" in data and isinstance(data["vector_db_path"], str):
            data["vector_db_path"] = Path(data["vector_db_path"])
        return cls(**data)

    def save(self, path: Path) -> None:
        """Save config to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "RAGConfig":
        """Load config from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
