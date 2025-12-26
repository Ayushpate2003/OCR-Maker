"""
Embedding generation for RAG.

Handles:
- Multiple embedding model support
- Batch processing
- Efficient caching
"""

from typing import List, Optional
from enum import Enum
import numpy as np


class EmbeddingModel(Enum):
    """Available embedding models."""

    # Efficient models
    MINILM_L6_V2 = "all-MiniLM-L6-v2"  # 384-dim, fast
    MINILM_L12_V2 = "all-MiniLM-L12-v2"  # 384-dim
    MINILM_L6_V3 = "all-MiniLM-L6-v3"  # 384-dim

    # Larger models
    MPNET_BASE = "all-mpnet-base-v2"  # 768-dim, better quality
    MPNET_LARGE = "all-mpnet-large-v2"  # 768-dim

    # Multilingual
    MULTILINGUAL_L6_V2 = "sentence-transformers/paraphrase-multilingual-MiniLM-L6-v2"
    MULTILINGUAL_MPNET = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        batch_size: int = 32,
    ):
        """
        Initialize embedding generator.

        Args:
            model_name: HuggingFace model ID or EmbeddingModel enum value
            device: torch device ('cpu', 'cuda', 'mps')
            batch_size: Batch size for processing
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size

        # Load model
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts.

        Args:
            texts: List of text strings

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.embedding_dim)

        # Use model's batch processing
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings

    def embed_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text.

        Args:
            text: Text string

        Returns:
            numpy array of shape (embedding_dim,)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": self.device,
        }
