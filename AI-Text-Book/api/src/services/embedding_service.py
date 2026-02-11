"""
Embedding Service
Generates embeddings using OpenAI API with caching and error handling.
"""

import os
import time
import hashlib
from typing import List, Dict, Optional
import openai
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self):
        """Initialize the embedding service."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.cache: Dict[str, List[float]] = {}
        self.cache_enabled = os.getenv("EMBEDDING_CACHE_ENABLED", "true").lower() == "true"

        logger.info(f"Initialized EmbeddingService with model: {self.model}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    async def embed_text(
        self,
        text: str,
        retry_count: int = 3,
        retry_delay: float = 1.0,
    ) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed
            retry_count: Number of retry attempts
            retry_delay: Delay between retries (exponential backoff)

        Returns:
            Embedding vector (1536-dim for text-embedding-3-small)
        """
        # Check cache
        if self.cache_enabled:
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                logger.debug(f"Cache hit for text: {text[:50]}...")
                return self.cache[cache_key]

        # Generate embedding with retry
        for attempt in range(retry_count):
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model,
                )

                embedding = response.data[0].embedding

                # Cache result
                if self.cache_enabled:
                    self.cache[cache_key] = embedding

                logger.debug(f"Generated embedding for text: {text[:50]}...")
                return embedding

            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit, attempt {attempt + 1}/{retry_count}: {e}")
                if attempt < retry_count - 1:
                    delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Waiting {delay}s before retry...")
                    time.sleep(delay)
                else:
                    raise

            except openai.APIError as e:
                logger.error(f"OpenAI API error: {e}")
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
                else:
                    raise

            except Exception as e:
                logger.error(f"Unexpected error generating embedding: {e}")
                raise

        raise RuntimeError("Failed to generate embedding after all retries")

    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(texts) + batch_size - 1) // batch_size}")

            # Process batch
            batch_embeddings = []
            for text in batch:
                embedding = await self.embed_text(text)
                batch_embeddings.append(embedding)

                # Rate limiting: wait between requests
                time.sleep(0.1)  # 10 requests/second limit

            embeddings.extend(batch_embeddings)

        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    def clear_cache(self):
        """Clear the embedding cache."""
        self.cache.clear()
        logger.info("Embedding cache cleared")

    def get_cache_size(self) -> int:
        """Get the number of cached embeddings."""
        return len(self.cache)


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the singleton embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
