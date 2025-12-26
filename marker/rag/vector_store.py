"""
Vector database interface and ChromaDB implementation.

Handles:
- Persistent vector storage
- Document indexing with metadata
- Similarity search
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import numpy as np
from pathlib import Path


@dataclass
class SearchResult:
    """Result from vector search."""

    chunk_text: str
    similarity_score: float
    metadata: Dict
    chunk_index: int
    filename: str


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict],
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents with embeddings."""
        pass

    @abstractmethod
    def search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> List[SearchResult]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete entire collection."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from collection."""
        pass


class ChromaVectorStore(VectorStore):
    """ChromaDB-based vector store implementation."""

    def __init__(
        self,
        db_path: Path = Path("./data/chroma_db"),
        collection_name: str = "marker_documents",
        embedding_dim: Optional[int] = None,
    ):
        """
        Initialize ChromaDB vector store.

        Args:
            db_path: Path to ChromaDB storage directory
            collection_name: Name of the collection
            embedding_dim: Dimension of embeddings (auto-detected if None)
        """
        try:
            import chromadb
        except ImportError:
            raise ImportError(
                "chromadb not installed. Install with: pip install chromadb"
            )

        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name

        # Initialize Chroma client with persistent storage
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self.embedding_dim = embedding_dim

    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict],
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Add documents with embeddings to the collection.

        Args:
            texts: List of text chunks
            embeddings: numpy array of embeddings (n, embedding_dim)
            metadatas: List of metadata dicts
            ids: Optional list of document IDs
        """
        if not texts:
            return

        # Generate IDs if not provided
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(texts))]

        # Convert embeddings to list of lists for Chroma
        embeddings_list = embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings

        # Add to collection
        self.collection.add(
            documents=texts,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids,
        )

    def search(
        self, query_embedding: np.ndarray, top_k: int = 5
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of SearchResult objects
        """
        # Convert to list for Chroma
        query_embedding_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding_list],
            n_results=top_k,
        )

        if not results or not results["documents"] or not results["documents"][0]:
            return []

        search_results = []
        for i in range(len(results["documents"][0])):
            result = SearchResult(
                chunk_text=results["documents"][0][i],
                similarity_score=1 - results["distances"][0][i],  # Convert distance to similarity
                metadata=results["metadatas"][0][i],
                chunk_index=results["metadatas"][0][i].get("chunk_index", 0),
                filename=results["metadatas"][0][i].get("filename", "unknown"),
            )
            search_results.append(result)

        return search_results

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def clear(self) -> None:
        """Clear all documents (equivalent to delete and recreate)."""
        self.delete_collection()

    def get_stats(self) -> Dict:
        """Get collection statistics."""
        return {
            "collection_name": self.collection_name,
            "document_count": self.collection.count(),
            "db_path": str(self.db_path),
        }
