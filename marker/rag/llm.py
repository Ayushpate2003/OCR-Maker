"""
LLM integration for RAG answer generation.

Handles:
- Ollama model communication
- Prompt construction
- Response generation with citations
"""

from dataclasses import dataclass
from typing import List, Optional
import requests
import json
from .retrieval import RetrievalResult
from .vector_store import SearchResult


@dataclass
class QueryResult:
    """Result from LLM query."""

    query: str
    answer: str
    sources: List[SearchResult]
    model: str
    tokens_used: int
    confidence: float  # 0-1 based on retrieval scores


class OllamaLLM:
    """Interface to Ollama local LLM."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma2:2b",
        temperature: float = 0.3,
        max_tokens: int = 512,
        context_window: int = 2048,
    ):
        """
        Initialize Ollama LLM.

        Args:
            base_url: Ollama API base URL
            model: Model name (e.g., "gemma2:2b", "llama2")
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            context_window: Model's context window size
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window

    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False

            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            return any(self.model in name for name in model_names)
        except Exception:
            return False

    def _construct_prompt(self, retrieval_result: RetrievalResult) -> str:
        """
        Construct prompt with context and instructions.

        Args:
            retrieval_result: Retrieved chunks

        Returns:
            Formatted prompt string
        """
        # Format context from retrieved chunks
        context_sections = []
        for i, result in enumerate(retrieval_result.chunks, 1):
            section = f"[Source {i}: {result.filename} (Chunk {result.chunk_index})]"
            if result.metadata.get("heading"):
                section += f"\nHeading: {result.metadata.get('heading')}"
            section += f"\n{result.chunk_text}"
            context_sections.append(section)

        context = "\n\n".join(context_sections)

        prompt = f"""You are a helpful assistant answering questions based on provided document excerpts.

Answer the user's question using ONLY the information provided in the context below.
If the answer is not in the context, say "I don't have this information in the provided documents."
Be concise and cite which sources you use.

CONTEXT:
{context}

QUESTION: {retrieval_result.query}

ANSWER:"""

        return prompt

    def answer(self, retrieval_result: RetrievalResult) -> QueryResult:
        """
        Generate answer using retrieved chunks.

        Args:
            retrieval_result: Retrieved chunks from query

        Returns:
            QueryResult with answer and metadata
        """
        if not retrieval_result.chunks:
            return QueryResult(
                query=retrieval_result.query,
                answer="No relevant documents found for your query.",
                sources=[],
                model=self.model,
                tokens_used=0,
                confidence=0.0,
            )

        # Check Ollama availability
        if not self._check_availability():
            raise RuntimeError(
                f"Ollama not available at {self.base_url} or model '{self.model}' not found. "
                f"Please ensure Ollama is running and the model is pulled."
            )

        # Construct prompt
        prompt = self._construct_prompt(retrieval_result)

        # Call Ollama API
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "stream": False,
                },
                timeout=120,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Ollama API error: {response.text}")

            result = response.json()
            answer = result.get("response", "").strip()

            # Calculate confidence based on average similarity of sources
            if retrieval_result.chunks:
                avg_similarity = sum(r.similarity_score for r in retrieval_result.chunks) / len(
                    retrieval_result.chunks
                )
                confidence = min(1.0, avg_similarity * 1.5)  # Scale similarity to confidence
            else:
                confidence = 0.0

            return QueryResult(
                query=retrieval_result.query,
                answer=answer,
                sources=retrieval_result.chunks,
                model=self.model,
                tokens_used=result.get("eval_count", 0),
                confidence=confidence,
            )

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "Ollama request timed out. The model may be too large for your system. "
                "Try a smaller model."
            )
        except Exception as e:
            raise RuntimeError(f"Error calling Ollama: {str(e)}")

    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_window": self.context_window,
        }
