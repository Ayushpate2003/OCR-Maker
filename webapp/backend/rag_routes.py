"""
FastAPI backend for RAG system.

Provides API endpoints for:
- Document indexing
- Query and answer generation
- RAG status and configuration
- Document management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging
import asyncio
from pathlib import Path
import json
from enum import Enum

from marker.rag.config import RAGConfig
from marker.rag.indexer import RAGIndexer
from marker.rag.retrieval import Retriever
from marker.rag.llm import OllamaLLM
from marker.rag.vector_store import ChromaVectorStore
from marker.rag.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================


class ChunkMetadataModel(BaseModel):
    """Metadata for a text chunk."""

    filename: str
    chunk_index: int
    heading: Optional[str] = None
    section: Optional[str] = None
    page_number: Optional[int] = None
    total_chunks: Optional[int] = None


class RetrievedChunkModel(BaseModel):
    """Retrieved chunk with metadata."""

    chunk_text: str
    similarity_score: float
    metadata: ChunkMetadataModel
    chunk_index: int
    filename: str


class IndexRequest(BaseModel):
    """Request to index documents."""

    file_path: str = Field(..., description="Path to markdown or json file")
    clear_existing: bool = Field(False, description="Clear existing index before indexing")


class IndexResponse(BaseModel):
    """Response from indexing."""

    status: str
    filename: str
    chunks_created: int
    message: str


class QueryRequest(BaseModel):
    """Request for RAG query."""

    query: str = Field(..., description="User question")
    top_k: Optional[int] = Field(5, description="Number of chunks to retrieve")
    include_chunks: bool = Field(True, description="Include retrieved chunks in response")


class SourceModel(BaseModel):
    """Source document reference."""

    filename: str
    chunk_index: int
    heading: Optional[str] = None
    similarity_score: float
    excerpt: str = Field(..., description="First 200 chars of chunk")


class QueryResponse(BaseModel):
    """Response from RAG query."""

    query: str
    answer: str
    sources: List[SourceModel]
    model: str
    tokens_used: int
    confidence: float
    retrieved_chunks: Optional[List[RetrievedChunkModel]] = None


class ConfigResponse(BaseModel):
    """Current RAG configuration."""

    enabled: bool
    chunk_size: int
    chunk_overlap: int
    embedding_model: str
    ollama_model: str
    top_k: int
    vector_db_path: str
    collection_name: str


class StatsResponse(BaseModel):
    """RAG system statistics."""

    vector_store: Dict
    embedding_model: Dict
    config: Dict


class HealthResponse(BaseModel):
    """Health check response."""

    rag_enabled: bool
    embeddings_model_available: bool
    vector_store_ready: bool
    ollama_available: bool
    message: str


# ============================================================================
# Global RAG State
# ============================================================================


class RAGState:
    """Maintains global RAG system state."""

    def __init__(self):
        self.config = None
        self.indexer = None
        self.retriever = None
        self.llm = None
        self.initialized = False

    def initialize(self, config: RAGConfig):
        """Initialize RAG system with config."""
        try:
            self.config = config
            self.indexer = RAGIndexer(config)

            # Initialize retriever
            vector_store = ChromaVectorStore(
                db_path=config.vector_db_path,
                collection_name=config.collection_name,
            )
            embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
            self.retriever = Retriever(
                vector_store=vector_store,
                embedding_generator=embedding_generator,
                top_k=config.top_k,
                similarity_threshold=config.similarity_threshold,
            )

            # Initialize LLM
            self.llm = OllamaLLM(
                base_url=config.ollama_base_url,
                model=config.ollama_model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

            self.initialized = True
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}")
            raise


rag_state = RAGState()


# ============================================================================
# Router
# ============================================================================


def create_rag_router(config: RAGConfig) -> APIRouter:
    """
    Create RAG API router.

    Args:
        config: RAGConfig instance

    Returns:
        APIRouter with RAG endpoints
    """
    router = APIRouter(prefix="/api/rag", tags=["RAG"])

    # Initialize RAG system
    rag_state.initialize(config)

    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """Check RAG system health."""
        try:
            # Check embeddings
            embeddings_available = True
            try:
                _ = rag_state.indexer.embedding_generator.get_model_info()
            except Exception:
                embeddings_available = False

            # Check vector store
            vector_store_ready = rag_state.indexer.vector_store is not None

            # Check Ollama
            ollama_available = rag_state.llm._check_availability()

            return HealthResponse(
                rag_enabled=rag_state.config.enabled,
                embeddings_model_available=embeddings_available,
                vector_store_ready=vector_store_ready,
                ollama_available=ollama_available,
                message="RAG system operational" if all([embeddings_available, vector_store_ready, ollama_available]) else "Some components unavailable",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/index", response_model=IndexResponse)
    async def index_document(request: IndexRequest, background_tasks: BackgroundTasks):
        """
        Index a document for RAG.

        Args:
            request: IndexRequest with file path
            background_tasks: FastAPI background tasks

        Returns:
            IndexResponse with results
        """
        try:
            file_path = Path(request.file_path)

            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

            # Clear if requested
            if request.clear_existing:
                rag_state.indexer.clear()
                logger.info("Cleared existing index")

            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Index
            if file_path.suffix.lower() == ".json":
                chunks = rag_state.indexer.index_json_output(content, file_path.name)
            else:
                chunks = rag_state.indexer.index_markdown(content, file_path.name)

            return IndexResponse(
                status="success",
                filename=file_path.name,
                chunks_created=chunks,
                message=f"Successfully indexed {chunks} chunks from {file_path.name}",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Indexing error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        """
        Query documents and get RAG answer.

        Args:
            request: QueryRequest with question

        Returns:
            QueryResponse with answer and sources
        """
        try:
            if not request.query.strip():
                raise HTTPException(status_code=400, detail="Query cannot be empty")

            # Retrieve relevant chunks
            retrieval_result = rag_state.retriever.retrieve(request.query, top_k=request.top_k)

            if not retrieval_result.chunks:
                return QueryResponse(
                    query=request.query,
                    answer="No relevant documents found for your query.",
                    sources=[],
                    model=rag_state.config.ollama_model,
                    tokens_used=0,
                    confidence=0.0,
                    retrieved_chunks=[] if request.include_chunks else None,
                )

            # Get LLM answer
            query_result = rag_state.llm.answer(retrieval_result)

            # Convert sources
            sources = [
                SourceModel(
                    filename=chunk.filename,
                    chunk_index=chunk.chunk_index,
                    heading=chunk.metadata.get("heading"),
                    similarity_score=chunk.similarity_score,
                    excerpt=chunk.chunk_text[:200] + "..." if len(chunk.chunk_text) > 200 else chunk.chunk_text,
                )
                for chunk in query_result.sources
            ]

            # Convert retrieved chunks if requested
            retrieved_chunks = None
            if request.include_chunks:
                retrieved_chunks = [
                    RetrievedChunkModel(
                        chunk_text=chunk.chunk_text,
                        similarity_score=chunk.similarity_score,
                        metadata=ChunkMetadataModel(**chunk.metadata),
                        chunk_index=chunk.chunk_index,
                        filename=chunk.filename,
                    )
                    for chunk in query_result.sources
                ]

            return QueryResponse(
                query=request.query,
                answer=query_result.answer,
                sources=sources,
                model=query_result.model,
                tokens_used=query_result.tokens_used,
                confidence=query_result.confidence,
                retrieved_chunks=retrieved_chunks,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/config", response_model=ConfigResponse)
    async def get_config():
        """Get current RAG configuration."""
        try:
            return ConfigResponse(
                enabled=rag_state.config.enabled,
                chunk_size=rag_state.config.chunk_size,
                chunk_overlap=rag_state.config.chunk_overlap,
                embedding_model=rag_state.config.embedding_model,
                ollama_model=rag_state.config.ollama_model,
                top_k=rag_state.config.top_k,
                vector_db_path=str(rag_state.config.vector_db_path),
                collection_name=rag_state.config.collection_name,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.put("/config")
    async def update_config(config_updates: dict):
        """
        Update RAG configuration.

        Args:
            config_updates: Dictionary of config updates

        Returns:
            Updated config
        """
        try:
            # Update allowed fields
            allowed_fields = [
                "chunk_size",
                "chunk_overlap",
                "top_k",
                "similarity_threshold",
                "ollama_model",
                "temperature",
                "max_tokens",
            ]

            for field, value in config_updates.items():
                if field in allowed_fields and hasattr(rag_state.config, field):
                    setattr(rag_state.config, field, value)

            # Update retriever if needed
            if "top_k" in config_updates:
                rag_state.retriever.top_k = rag_state.config.top_k
            if "similarity_threshold" in config_updates:
                rag_state.retriever.similarity_threshold = rag_state.config.similarity_threshold
            if "ollama_model" in config_updates:
                rag_state.llm.model = rag_state.config.ollama_model

            logger.info(f"Updated RAG config: {config_updates}")
            return await get_config()

        except Exception as e:
            logger.error(f"Config update error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/stats", response_model=StatsResponse)
    async def get_stats():
        """Get RAG system statistics."""
        try:
            return StatsResponse(**rag_state.indexer.get_stats())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/clear")
    async def clear_index():
        """Clear all indexed documents."""
        try:
            rag_state.indexer.clear()
            logger.info("Index cleared")
            return {"status": "success", "message": "Index cleared"}
        except Exception as e:
            logger.error(f"Clear error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    return router
