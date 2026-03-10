"""
RAG Retrieval Service
Handles vector search and reranking for the RAG pipeline.
"""

from typing import List, Dict, Any, Optional
import logging
from db.qdrant_client import qdrant_client

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving and reranking relevant chunks."""

    def __init__(
        self,
        top_k: int = 50,
        score_threshold: float = 0.2,
        rerank_top_n: int = 15,
    ):
        """
        Initialize the retrieval service.

        Args:
            top_k: Number of initial chunks to retrieve
            score_threshold: Minimum similarity score threshold
            rerank_top_n: Number of chunks to return after reranking
        """
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.rerank_top_n = rerank_top_n
        logger.info(
            f"Initialized RetrievalService (top_k={top_k}, "
            f"threshold={score_threshold}, rerank_top_n={rerank_top_n})"
        )

    @staticmethod
    def build_qdrant_filter(filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        T100 — Build a structured Qdrant filter payload from caller-supplied metadata
        to narrow the search space BEFORE vector scoring (pre-filtering).

        Only non-None filter values produce conditions. Supported keys:
          - chapter: exact string match on payload.chapter
          - section: exact string match on payload.section
          - heading: exact string match on payload.heading
          - page_number: exact integer match on payload.page_number
          - page_range: dict with 'gte' and/or 'lte' for integer range

        Returns a Qdrant REST filter dict, or None if no valid conditions found.
        """
        must_conditions = []

        # Exact-match conditions
        for field in ("chapter", "section", "heading"):
            val = filters.get(field)
            if val:
                must_conditions.append({
                    "key": field,
                    "match": {"value": str(val)},
                })

        # Exact page number
        page = filters.get("page_number")
        if page is not None:
            must_conditions.append({
                "key": "page_number",
                "match": {"value": int(page)},
            })

        # Page range (e.g. {"gte": 10, "lte": 25})
        page_range = filters.get("page_range")
        if isinstance(page_range, dict):
            range_cond: Dict[str, Any] = {"key": "page_number", "range": {}}
            if "gte" in page_range:
                range_cond["range"]["gte"] = int(page_range["gte"])
            if "lte" in page_range:
                range_cond["range"]["lte"] = int(page_range["lte"])
            if range_cond["range"]:
                must_conditions.append(range_cond)

        if not must_conditions:
            return None

        return {"must": must_conditions}

    async def retrieve(
        self,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using vector search.

        T100: Converts *filters* into a structured Qdrant pre-filter before the
        vector search, reducing the candidate space and improving latency.

        Args:
            query_embedding: Query embedding vector
            filters: Optional metadata filters (e.g., chapter, section)

        Returns:
            List of relevant chunks with scores and metadata
        """
        try:
            # T100 — Build pre-filter from metadata dict
            qdrant_filter = self.build_qdrant_filter(filters) if filters else None

            logger.debug(
                f"Retrieving top {self.top_k} chunks "
                f"(threshold={self.score_threshold}, "
                f"pre_filter={'yes' if qdrant_filter else 'none'})"
            )

            # Search Qdrant with pre-filter applied
            results = await qdrant_client.search(
                query_vector=query_embedding,
                top_k=self.top_k,
                score_threshold=self.score_threshold,
                metadata_filter=qdrant_filter,
            )

            logger.info(f"Retrieved {len(results)} chunks from vector search")
            return results

        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            raise

    def rerank(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Rerank retrieved chunks using multiple signals.

        Reranking strategy:
        1. Semantic similarity score (from vector search)
        2. Text overlap with query (keyword matching)
        3. Chunk metadata quality (completeness)

        Args:
            chunks: Retrieved chunks with scores
            query: Original user query

        Returns:
            Reranked top-n chunks
        """
        if not chunks:
            logger.warning("No chunks to rerank")
            return []

        logger.debug(f"Reranking {len(chunks)} chunks")

        # Extract technical terms from query: function names (foo()), identifiers
        # (foo_bar), and significant words (> 4 chars).  These are boosted when
        # found verbatim in a chunk so that code-heavy content ranks higher.
        import re as _re
        tech_terms = [
            t.strip("()") for t in _re.findall(r'\b\w[\w_]*(?:\(\))?\b', query)
            if len(t.strip("()")) > 4
        ]

        # Calculate reranking scores
        reranked = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for chunk in chunks:
            # Base score from vector similarity
            vector_score = chunk.get("score", 0.0)

            # Text overlap score (keyword matching)
            chunk_text = chunk.get("text", "").lower()
            chunk_words = set(chunk_text.split())
            overlap_score = len(query_words & chunk_words) / max(len(query_words), 1)

            # Technical term exact-match boost: rewards chunks that contain
            # specific function/identifier names from the query verbatim.
            # This surfaces code-heavy chunks that embeddings often miss.
            tech_hits = sum(1 for t in tech_terms if t.lower() in chunk_text)
            tech_boost = min(tech_hits / max(len(tech_terms), 1), 1.0)

            # Metadata completeness score
            metadata = chunk.get("metadata", {})
            metadata_score = sum([
                0.3 if metadata.get("chapter") else 0,
                0.3 if metadata.get("section") else 0,
                0.2 if metadata.get("heading") else 0,
                0.2 if metadata.get("page_number") else 0,
            ])

            # Combined reranking score (weighted average)
            rerank_score = (
                0.50 * vector_score +
                0.20 * overlap_score +
                0.20 * tech_boost +
                0.10 * metadata_score
            )

            chunk_with_rerank = {
                **chunk,
                "rerank_score": rerank_score,
                "vector_score": vector_score,
                "overlap_score": overlap_score,
                "tech_boost": tech_boost,
                "metadata_score": metadata_score,
            }
            reranked.append(chunk_with_rerank)

        # Sort by rerank score and take top-n
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        top_n = reranked[:self.rerank_top_n]

        logger.info(
            f"Reranked to top {len(top_n)} chunks "
            f"(scores: {[round(c['rerank_score'], 3) for c in top_n]})"
        )

        return top_n

    async def retrieve_and_rerank(
        self,
        query: str,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and rerank chunks in one step.

        Args:
            query: User query text
            query_embedding: Query embedding vector
            filters: Optional metadata filters

        Returns:
            Top-n reranked chunks
        """
        # Retrieve initial candidates
        chunks = await self.retrieve(query_embedding, filters)

        # Rerank to get top-n
        top_chunks = self.rerank(chunks, query)

        return top_chunks


# Singleton instance
_retrieval_service = None


def get_retrieval_service(
    top_k: int = 50,
    score_threshold: float = 0.2,
    rerank_top_n: int = 15,
) -> RetrievalService:
    """Get or create the singleton RetrievalService instance."""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService(
            top_k=top_k,
            score_threshold=score_threshold,
            rerank_top_n=rerank_top_n,
        )
    return _retrieval_service