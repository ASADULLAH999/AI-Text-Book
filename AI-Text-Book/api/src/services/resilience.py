"""
Resilience Utilities
T113 — Graceful degradation for Qdrant Cloud failures.
T114 — Retry logic with exponential backoff for OpenAI API.
T115 — Circuit breaker for database connections.
"""

import asyncio
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# T114 — Exponential backoff retry decorator
# ---------------------------------------------------------------------------

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    jitter: bool = True,
):
    """
    Async decorator that retries a coroutine with exponential backoff.

    Args:
        max_attempts: Maximum number of total attempts (including first).
        initial_delay: Seconds to wait before the first retry.
        backoff_factor: Multiplier applied to delay on each retry.
        max_delay: Upper bound on per-retry delay in seconds.
        retriable_exceptions: Only retry on these exception types.
        jitter: Add ±10% random jitter to avoid thundering herd.
    """
    import random

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exc: Optional[Exception] = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retriable_exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__}: all {max_attempts} attempts failed. "
                            f"Last error: {exc}"
                        )
                        raise

                    actual_delay = min(delay, max_delay)
                    if jitter:
                        actual_delay *= 1 + random.uniform(-0.1, 0.1)

                    logger.warning(
                        f"{func.__name__}: attempt {attempt}/{max_attempts} failed "
                        f"({type(exc).__name__}: {exc}). "
                        f"Retrying in {actual_delay:.2f}s…"
                    )
                    await asyncio.sleep(actual_delay)
                    delay *= backoff_factor

            raise  # unreachable but satisfies type checkers

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# T115 — Circuit breaker
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Blocking all calls
    HALF_OPEN = "half_open" # Probing with single call


class CircuitBreaker:
    """
    Circuit breaker for protecting downstream dependencies (Qdrant, Postgres).

    States:
      CLOSED  → calls pass through; failure_count incremented on error.
      OPEN    → all calls blocked; transitions to HALF_OPEN after reset_timeout.
      HALF_OPEN → one probe call allowed; on success → CLOSED; on failure → OPEN.

    Args:
        failure_threshold: Consecutive failures to open the circuit.
        reset_timeout: Seconds in OPEN state before trying HALF_OPEN.
        name: Label for logging.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        name: str = "circuit",
    ) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.name = name

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        return self._state

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._last_failure_time = time.monotonic()
        logger.error(
            f"CircuitBreaker[{self.name}] OPEN after "
            f"{self._failure_count} consecutive failures"
        )

    def _reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        logger.info(f"CircuitBreaker[{self.name}] CLOSED (recovered)")

    def _maybe_probe(self) -> bool:
        """Return True if enough time has passed to probe from OPEN."""
        elapsed = time.monotonic() - self._last_failure_time
        return elapsed >= self.reset_timeout

    # ------------------------------------------------------------------
    # Public call interface
    # ------------------------------------------------------------------

    async def call(self, coro_factory: Callable, *args, **kwargs) -> Any:
        """
        Execute *coro_factory(*args, **kwargs)* guarded by the circuit breaker.

        Raises:
            RuntimeError: If circuit is OPEN.
            Any exception from the coroutine on failure.
        """
        async with self._lock:
            if self._state == CircuitState.OPEN:
                if self._maybe_probe():
                    self._state = CircuitState.HALF_OPEN
                    logger.info(
                        f"CircuitBreaker[{self.name}] HALF_OPEN — probing…"
                    )
                else:
                    raise RuntimeError(
                        f"CircuitBreaker[{self.name}] is OPEN — "
                        f"call rejected to protect downstream service."
                    )

        try:
            result = await coro_factory(*args, **kwargs)

            async with self._lock:
                if self._state == CircuitState.HALF_OPEN:
                    self._reset()
                elif self._state == CircuitState.CLOSED:
                    self._failure_count = 0  # reset on success

            return result

        except Exception as exc:
            async with self._lock:
                self._failure_count += 1
                if (
                    self._state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)
                    and self._failure_count >= self.failure_threshold
                ):
                    self._trip()
            raise exc

    @property
    def status(self) -> dict:
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "reset_timeout_seconds": self.reset_timeout,
        }


# ---------------------------------------------------------------------------
# T113 — Graceful degradation helpers
# ---------------------------------------------------------------------------

async def with_fallback(primary_coro, fallback_coro, label: str = "operation"):
    """
    Try *primary_coro*; on any exception, log a warning and run *fallback_coro*.

    Typical use: Qdrant vector search → BM25 keyword fallback.
    """
    try:
        return await primary_coro
    except Exception as exc:
        logger.warning(
            f"T113 graceful degradation [{label}]: primary failed ({exc}), "
            f"using fallback."
        )
        return await fallback_coro


# ---------------------------------------------------------------------------
# Pre-built circuit breakers (singletons)
# ---------------------------------------------------------------------------

_qdrant_cb: Optional[CircuitBreaker] = None
_postgres_cb: Optional[CircuitBreaker] = None


def get_qdrant_circuit_breaker() -> CircuitBreaker:
    global _qdrant_cb
    if _qdrant_cb is None:
        _qdrant_cb = CircuitBreaker(
            failure_threshold=5,
            reset_timeout=60.0,
            name="qdrant",
        )
    return _qdrant_cb


def get_postgres_circuit_breaker() -> CircuitBreaker:
    global _postgres_cb
    if _postgres_cb is None:
        _postgres_cb = CircuitBreaker(
            failure_threshold=3,
            reset_timeout=30.0,
            name="postgres",
        )
    return _postgres_cb
