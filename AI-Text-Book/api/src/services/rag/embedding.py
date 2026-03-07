"""
RAG Query Embedding Service
Handles query embedding for semantic search in the RAG pipeline.
"""

from typing import List
import logging
from services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class QueryEmbeddingService:
    """Service for embedding user queries for semantic search."""

    def __init__(self):
        """Initialize the query embedding service."""
        self._embedding_service = get_embedding_service()
        logger.info("Initialized QueryEmbeddingService")

    async def embed_query(self, query: str) -> List[float]:
        """
        Embed a user query for semantic search.

        Args:
            query: User query text

        Returns:
            Query embedding vector (1536 dimensions for text-embedding-3-small)

        Raises:
            ValueError: If query is empty or invalid
            Exception: If embedding generation fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Truncate very long queries (OpenAI limit is ~8191 tokens)
        max_chars = 8000
        if len(query) > max_chars:
            logger.warning(f"Query truncated from {len(query)} to {max_chars} chars")
            query = query[:max_chars]

        try:
            logger.debug(f"Embedding query: {query[:100]}...")
            embedding = await self._embedding_service.embed_text(query)
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise

    async def embed_queries(self, queries: List[str]) -> List[List[float]]:
        """
        Embed multiple queries in batch.

        Args:
            queries: List of query texts

        Returns:
            List of query embedding vectors

        Raises:
            ValueError: If queries list is empty
            Exception: If embedding generation fails
        """
        if not queries:
            raise ValueError("Queries list cannot be empty")

        logger.info(f"Embedding {len(queries)} queries")

        embeddings = []
        for query in queries:
            embedding = await self.embed_query(query)
            embeddings.append(embedding)

        logger.info(f"Successfully embedded {len(embeddings)} queries")
        return embeddings


# Singleton instance
_query_embedding_service = None


def get_query_embedding_service() -> QueryEmbeddingService:
    """Get or create the singleton QueryEmbeddingService instance."""
    global _query_embedding_service
    if _query_embedding_service is None:
        _query_embedding_service = QueryEmbeddingService()
    return _query_embedding_service
