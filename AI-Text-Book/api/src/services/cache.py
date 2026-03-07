"""
Query Result Cache
T098 [P] — In-process TTL cache for RAG query results.
T101     — Request coalescing for duplicate in-flight queries.

Design:
- LRU cache with configurable TTL and max size (avoids unbounded memory).
- Coalescing: if the same query arrives while the first is in-flight,
  the second awaits the same Future instead of launching a duplicate pipeline.
- Cache key: SHA-256 of (query, mode, tone, filters) — deterministic, collision-safe.
- Serverless-safe: each Vercel Function instance has its own in-process cache;
  no Redis required for correctness (only for cross-instance sharing, opt-in).
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import OrderedDict
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache entry dataclass
# ---------------------------------------------------------------------------

class _CacheEntry:
    __slots__ = ("value", "expires_at", "hits")

    def __init__(self, value: Any, ttl_seconds: int) -> None:
        self.value = value
        self.expires_at = time.monotonic() + ttl_seconds
        self.hits = 0

    @property
    def is_expired(self) -> bool:
        return time.monotonic() > self.expires_at


# ---------------------------------------------------------------------------
# TTL LRU Cache
# ---------------------------------------------------------------------------

class QueryCache:
    """
    Thread-safe (asyncio) LRU cache with per-entry TTL.

    T098: caches final RAG responses keyed by query fingerprint.
    T101: `get_or_set_coalesced` prevents duplicate pipeline executions.
    """

    def __init__(self, max_size: int = 512, ttl_seconds: int = 300) -> None:
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._store: OrderedDict[str, _CacheEntry] = OrderedDict()
        # T101 — in-flight futures per cache key
        self._in_flight: dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    # ------------------------------------------------------------------
    # Low-level get / set
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or None if missing/expired."""
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        if entry.is_expired:
            del self._store[key]
            self._misses += 1
            return None
        # LRU: move to end
        self._store.move_to_end(key)
        entry.hits += 1
        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any) -> None:
        """Store value under key, evicting LRU entries if needed."""
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = _CacheEntry(value, self._ttl)
        if len(self._store) > self._max_size:
            evicted_key, _ = self._store.popitem(last=False)
            logger.debug(f"Cache evicted LRU entry: {evicted_key[:16]}…")

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
        self._in_flight.clear()

    # ------------------------------------------------------------------
    # T101 — Request coalescing
    # ------------------------------------------------------------------

    async def get_or_set_coalesced(self, key: str, coro_factory) -> Any:
        """
        Return cached value if present; otherwise run *coro_factory()* exactly
        once, cache the result, and return it to all concurrent waiters.

        If N requests arrive with the same key while the first is in-flight,
        they all await the same Future — no duplicate pipeline executions.
        """
        # Fast path — cache hit (no lock needed for read)
        cached = self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit: {key[:16]}…")
            return cached

        async with self._lock:
            # Double-check after acquiring lock
            cached = self.get(key)
            if cached is not None:
                return cached

            # Check if already in-flight
            if key in self._in_flight:
                future = self._in_flight[key]
            else:
                # Start the coroutine; register the future
                loop = asyncio.get_event_loop()
                future: asyncio.Future = loop.create_future()
                self._in_flight[key] = future

                async def _run():
                    try:
                        result = await coro_factory()
                        self.set(key, result)
                        future.set_result(result)
                    except Exception as exc:
                        future.set_exception(exc)
                    finally:
                        self._in_flight.pop(key, None)

                asyncio.ensure_future(_run())

        # Await outside lock so other coroutines can progress
        return await asyncio.shield(future)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total else 0.0

    @property
    def stats(self) -> dict:
        return {
            "size": len(self._store),
            "max_size": self._max_size,
            "ttl_seconds": self._ttl,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate, 4),
            "in_flight": len(self._in_flight),
        }


# ---------------------------------------------------------------------------
# Cache key builder
# ---------------------------------------------------------------------------

def build_cache_key(
    query: str,
    mode: str,
    tone: Optional[str] = None,
    filters: Optional[dict] = None,
) -> str:
    """
    Build a deterministic SHA-256 cache key from query parameters.

    Args:
        query: User question text.
        mode: Answering mode (book_only, selected_text, general_knowledge).
        tone: Optional tone string.
        filters: Optional metadata filters dict.

    Returns:
        64-character hex digest.
    """
    payload = {
        "q": query.strip().lower(),
        "m": mode,
        "t": tone or "neutral",
        "f": filters or {},
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

import os

_cache: Optional[QueryCache] = None


def get_query_cache() -> QueryCache:
    """Return the singleton QueryCache instance."""
    global _cache
    if _cache is None:
        max_size = int(os.getenv("CACHE_MAX_SIZE", "512"))
        ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", "300"))
        _cache = QueryCache(max_size=max_size, ttl_seconds=ttl_seconds)
        logger.info(f"QueryCache initialized (max={max_size}, ttl={ttl_seconds}s)")
    return _cache
