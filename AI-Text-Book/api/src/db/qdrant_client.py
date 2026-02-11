"""
Qdrant Vector Database Client
Manages connections to Qdrant Cloud for semantic search operations.
"""

import os
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
)
import logging

logger = logging.getLogger(__name__)


class QdrantClientSingleton:
    """Singleton wrapper for Qdrant client with connection pooling and error handling."""

    _instance: Optional[QdrantClient] = None
    _collection_name: str = ""

    @classmethod
    def get_client(cls) -> QdrantClient:
        """Get or create Qdrant client instance."""
        if cls._instance is None:
            try:
                qdrant_url = os.getenv("QDRANT_URL")
                qdrant_api_key = os.getenv("QDRANT_API_KEY")
                cls._collection_name = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")

                if not qdrant_url or not qdrant_api_key:
                    raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")

                cls._instance = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    timeout=10.0,
                )

                logger.info(f"Connected to Qdrant at {qdrant_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise

        return cls._instance

    @classmethod
    def get_collection_name(cls) -> str:
        """Get the collection name."""
        if not cls._collection_name:
            cls.get_client()  # Initialize if needed
        return cls._collection_name

    @classmethod
    async def ensure_collection_exists(cls) -> bool:
        """Ensure the collection exists, create if it doesn't."""
        try:
            client = cls.get_client()
            collection_name = cls.get_collection_name()

            # Check if collection exists
            collections = client.get_collections()
            exists = any(c.name == collection_name for c in collections.collections)

            if not exists:
                # Create collection with 1536-dimensional vectors (OpenAI embeddings)
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1536,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.info(f"Collection already exists: {collection_name}")

            return True
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    @classmethod
    async def search(
        cls,
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant.

        Args:
            query_vector: Query embedding vector (1536-dim)
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            metadata_filter: Optional metadata filters (e.g., {"chapter": "Introduction"})

        Returns:
            List of search results with chunk_id, score, and metadata
        """
        try:
            client = cls.get_client()
            collection_name = cls.get_collection_name()

            # Build filter if metadata provided
            search_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                search_filter = Filter(must=conditions)

            # Perform search
            results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            # Format results
            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "chunk_id": hit.payload.get("chunk_id"),
                    "text": hit.payload.get("text"),
                    "score": hit.score,
                    "metadata": {
                        "chapter": hit.payload.get("chapter"),
                        "section": hit.payload.get("section"),
                        "heading": hit.payload.get("heading"),
                        "page_number": hit.payload.get("page_number"),
                    },
                })

            logger.info(f"Retrieved {len(formatted_results)} chunks with scores >= {score_threshold}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            raise

    @classmethod
    async def upsert_chunks(
        cls,
        chunks: List[Dict[str, Any]],
    ) -> int:
        """
        Upsert chunks into Qdrant.

        Args:
            chunks: List of chunk dictionaries with 'chunk_id', 'text', 'embedding', and 'metadata'

        Returns:
            Number of chunks upserted
        """
        try:
            client = cls.get_client()
            collection_name = cls.get_collection_name()

            # Convert chunks to Qdrant points
            points = []
            for chunk in chunks:
                point = PointStruct(
                    id=chunk["chunk_id"],
                    vector=chunk["embedding"],
                    payload={
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "chapter": chunk["metadata"].get("chapter"),
                        "section": chunk["metadata"].get("section"),
                        "heading": chunk["metadata"].get("heading"),
                        "page_number": chunk["metadata"].get("page_number"),
                    },
                )
                points.append(point)

            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                client.upsert(
                    collection_name=collection_name,
                    points=batch,
                )

            logger.info(f"Upserted {len(points)} chunks to Qdrant")
            return len(points)

        except Exception as e:
            logger.error(f"Error upserting chunks to Qdrant: {e}")
            raise

    @classmethod
    async def get_chunk_by_id(cls, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chunk by ID."""
        try:
            client = cls.get_client()
            collection_name = cls.get_collection_name()

            result = client.retrieve(
                collection_name=collection_name,
                ids=[chunk_id],
            )

            if result:
                point = result[0]
                return {
                    "chunk_id": point.payload.get("chunk_id"),
                    "text": point.payload.get("text"),
                    "metadata": {
                        "chapter": point.payload.get("chapter"),
                        "section": point.payload.get("section"),
                        "heading": point.payload.get("heading"),
                        "page_number": point.payload.get("page_number"),
                    },
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving chunk {chunk_id}: {e}")
            raise

    @classmethod
    def close(cls):
        """Close the Qdrant client connection."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("Closed Qdrant connection")


# Export singleton instance
qdrant_client = QdrantClientSingleton()
