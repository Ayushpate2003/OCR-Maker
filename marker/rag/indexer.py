"""
Main RAG indexing pipeline.

Coordinates:
- Document loading from Marker output
- Chunking
- Embedding generation
- Vector store indexing
"""

import json
from pathlib import Path
from typing import List, Optional, Union
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import RAGConfig
from .chunking import SemanticChunker
from .embeddings import EmbeddingGenerator
from .vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class RAGIndexer:
    """Main indexing pipeline for RAG."""

    def __init__(self, config: RAGConfig):
        """
        Initialize RAG indexer.

        Args:
            config: RAGConfig instance
        """
        self.config = config

        # Initialize components
        self.chunker = SemanticChunker(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            min_chunk_size=config.min_chunk_size,
        )

        self.embedding_generator = EmbeddingGenerator(
            model_name=config.embedding_model,
            batch_size=config.batch_size,
        )

        self.vector_store = ChromaVectorStore(
            db_path=config.vector_db_path,
            collection_name=config.collection_name,
            embedding_dim=config.embedding_dimension,
        )

    def index_markdown(
        self,
        markdown_text: str,
        filename: str,
        page_number: Optional[int] = None,
    ) -> int:
        """
        Index a Markdown document.

        Args:
            markdown_text: Markdown content
            filename: Document filename
            page_number: Optional page number

        Returns:
            Number of chunks indexed
        """
        logger.info(f"Indexing markdown: {filename}")

        # Chunk the document
        chunks = self.chunker.chunk(
            text=markdown_text,
            filename=filename,
            page_number=page_number,
        )

        if not chunks:
            logger.warning(f"No chunks created from {filename}")
            return 0

        # Extract texts and metadatas
        texts = [chunk_text for chunk_text, _ in chunks]
        metadatas = [meta.to_dict() for _, meta in chunks]

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.embedding_generator.embed(texts)

        # Index in vector store
        self.vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=[f"{filename}_chunk_{i}" for i in range(len(texts))],
        )

        logger.info(f"Indexed {len(chunks)} chunks from {filename}")
        return len(chunks)

    def index_json_output(
        self,
        json_data: Union[str, dict],
        filename: str,
    ) -> int:
        """
        Index JSON output from Marker.

        Args:
            json_data: JSON content or dict
            filename: Document filename

        Returns:
            Number of chunks indexed
        """
        # Parse JSON if string
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        # Extract text from JSON structure
        # This assumes Marker's JSON output format with 'text' or 'content' fields
        text_content = self._extract_text_from_json(data)

        return self.index_markdown(text_content, filename)

    def _extract_text_from_json(self, data: dict) -> str:
        """
        Extract text from Marker's JSON output.

        Args:
            data: Marker JSON output

        Returns:
            Extracted text string
        """
        # Try common Marker JSON structures
        if isinstance(data, dict):
            # Check for direct text fields
            if "text" in data:
                return data["text"]
            if "content" in data:
                return data["content"]
            if "markdown" in data:
                return data["markdown"]

            # Recursively extract text from nested structures
            all_text = []
            for value in data.values():
                if isinstance(value, str):
                    all_text.append(value)
                elif isinstance(value, (dict, list)):
                    all_text.append(self._extract_text_from_json(value))

            return "\n\n".join(t for t in all_text if t)

        elif isinstance(data, list):
            all_text = []
            for item in data:
                if isinstance(item, str):
                    all_text.append(item)
                else:
                    all_text.append(self._extract_text_from_json(item))
            return "\n\n".join(t for t in all_text if t)

        return str(data) if data else ""

    def index_directory(self, directory: Path, pattern: str = "*.md") -> dict:
        """
        Index all documents in a directory.

        Args:
            directory: Path to directory with markdown/json files
            pattern: File pattern to match (default: "*.md")

        Returns:
            Dictionary with indexing results
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory}")

        files = list(directory.glob(pattern))
        logger.info(f"Found {len(files)} files matching {pattern}")

        results = {"total_files": len(files), "indexed_files": 0, "total_chunks": 0, "errors": []}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if file_path.suffix.lower() == ".json":
                    chunks = self.index_json_output(content, file_path.name)
                else:
                    chunks = self.index_markdown(content, file_path.name)

                results["indexed_files"] += 1
                results["total_chunks"] += chunks
                logger.info(f"✓ {file_path.name}: {chunks} chunks")

            except Exception as e:
                error_msg = f"Error indexing {file_path.name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        return results

    def clear(self) -> None:
        """Clear all indexed documents."""
        logger.info("Clearing vector store")
        self.vector_store.clear()

    def get_stats(self) -> dict:
        """Get indexing statistics."""
        return {
            "vector_store": self.vector_store.get_stats(),
            "embedding_model": self.embedding_generator.get_model_info(),
            "config": self.config.to_dict(),
        }
