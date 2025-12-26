#!/usr/bin/env python3
"""
Example: Query documents using the RAG system

This script demonstrates how to query indexed documents and get
answers from a local language model using retrieved context.
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
    from marker.rag.vector_store import ChromaVectorStore
    from marker.rag.embeddings import EmbeddingGenerator
    from marker.rag.retrieval import Retriever
    from marker.rag.llm import OllamaLLM
except ImportError:
    print("Error: RAG modules not installed. Run: pip install -r webapp/backend/requirements-rag.txt")
    sys.exit(1)


def main():
    """
    Query indexed documents and get answers
    """
    # Create config
    config = RAGConfig(
        chunk_size=800,
        chunk_overlap=100,
        embedding_model="all-MiniLM-L6-v2",
        vector_db_path=Path("./data/chroma_db"),
        ollama_base_url="http://localhost:11434",
        ollama_model="gemma2:2b",
        top_k=5,
    )

    print("🔍 RAG Query Example")
    print("=" * 50)
    print()

    # Initialize components
    print("Initializing RAG system...")
    vector_store = ChromaVectorStore(
        db_path=config.vector_db_path,
        collection_name=config.collection_name,
    )

    embedding_generator = EmbeddingGenerator(
        model_name=config.embedding_model
    )

    retriever = Retriever(
        vector_store=vector_store,
        embedding_generator=embedding_generator,
        top_k=config.top_k,
        similarity_threshold=config.similarity_threshold,
    )

    llm = OllamaLLM(
        base_url=config.ollama_base_url,
        model=config.ollama_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    print("✓ RAG system initialized")
    print()

    # Example queries
    queries = [
        "What is RAG?",
        "How does semantic chunking work?",
        "What embedding models are available?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 50)

        try:
            # Retrieve relevant chunks
            retrieval_result = retriever.retrieve(query)

            if not retrieval_result.chunks:
                print("No relevant documents found.")
                print()
                continue

            print(f"Retrieved {len(retrieval_result.chunks)} chunks:")
            for j, chunk in enumerate(retrieval_result.chunks, 1):
                print(f"  {j}. {chunk.filename} (score: {chunk.similarity_score:.2f})")
                if chunk.metadata.get("heading"):
                    print(f"     Heading: {chunk.metadata['heading']}")
            print()

            # Generate answer using LLM
            print("Generating answer...")
            query_result = llm.answer(retrieval_result)

            print(f"Answer: {query_result.answer}")
            print()
            print(f"Model: {query_result.model}")
            print(f"Confidence: {query_result.confidence:.0%}")
            print(f"Tokens used: {query_result.tokens_used}")
            print()

        except Exception as e:
            print(f"Error: {str(e)}")
            print()

    print("✅ Query example complete!")


if __name__ == "__main__":
    main()
