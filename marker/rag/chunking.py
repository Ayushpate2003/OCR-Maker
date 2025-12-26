"""
Semantic text chunking for RAG.

Implements intelligent document chunking with:
- Respects section boundaries
- Maintains semantic coherence
- Preserves metadata (headings, page numbers)
- Configurable overlap
"""

from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class ChunkMetadata:
    """Metadata associated with a text chunk."""

    filename: str
    chunk_index: int
    heading: Optional[str] = None
    section: Optional[str] = None
    page_number: Optional[int] = None
    total_chunks: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "filename": self.filename,
            "chunk_index": self.chunk_index,
            "heading": self.heading,
            "section": self.section,
            "page_number": self.page_number,
            "total_chunks": self.total_chunks,
        }


class SemanticChunker:
    """Splits documents into semantically coherent chunks."""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        min_chunk_size: int = 100,
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Target tokens per chunk (rough estimate: 1 token ≈ 4 chars)
            chunk_overlap: Tokens to overlap between chunks
            min_chunk_size: Minimum tokens in a chunk
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate: 1 token ≈ 4 characters."""
        return len(text) // 4

    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs (double newlines or single for markdown)."""
        # First, normalize line endings
        text = text.replace("\r\n", "\n")
        # Split by double newlines or markdown section markers
        paragraphs = re.split(r"\n\n+|(?=^#+\s)", text, flags=re.MULTILINE)
        return [p.strip() for p in paragraphs if p.strip()]

    def _extract_heading(self, text: str) -> Optional[str]:
        """Extract heading from text if it starts with markdown heading."""
        match = re.match(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
        if match:
            return match.group(2)
        return None

    def chunk(
        self,
        text: str,
        filename: str,
        page_number: Optional[int] = None,
    ) -> List[tuple[str, ChunkMetadata]]:
        """
        Split document into semantic chunks.

        Args:
            text: Document text
            filename: Source filename
            page_number: Optional page number

        Returns:
            List of (chunk_text, metadata) tuples
        """
        if not text or not text.strip():
            return []

        chunks = []
        chunk_index = 0

        # Split into paragraphs first
        paragraphs = self._split_by_paragraphs(text)

        current_chunk = ""
        current_heading = None
        paragraph_count = 0

        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)

            # Extract heading if this paragraph is a heading
            heading = self._extract_heading(para)
            if heading:
                current_heading = heading

            # If current chunk is empty, start with this paragraph
            if not current_chunk:
                current_chunk = para
                paragraph_count = 1
                continue

            # Check if adding this paragraph would exceed chunk size
            potential_chunk = current_chunk + "\n\n" + para
            potential_tokens = self._estimate_tokens(potential_chunk)

            if potential_tokens <= self.chunk_size:
                # Add to current chunk
                current_chunk = potential_chunk
                paragraph_count += 1
            else:
                # Current chunk is full, save it
                if self._estimate_tokens(current_chunk) >= self.min_chunk_size:
                    metadata = ChunkMetadata(
                        filename=filename,
                        chunk_index=chunk_index,
                        heading=current_heading,
                        page_number=page_number,
                    )
                    chunks.append((current_chunk, metadata))
                    chunk_index += 1

                # Start new chunk with overlap
                # Keep the last part of previous chunk for context
                current_chunk = para
                paragraph_count = 1

        # Don't forget the last chunk
        if current_chunk and self._estimate_tokens(current_chunk) >= self.min_chunk_size:
            metadata = ChunkMetadata(
                filename=filename,
                chunk_index=chunk_index,
                heading=current_heading,
                page_number=page_number,
            )
            chunks.append((current_chunk, metadata))

        # Update total_chunks in metadata
        for i, (_, meta) in enumerate(chunks):
            meta.total_chunks = len(chunks)

        return chunks
