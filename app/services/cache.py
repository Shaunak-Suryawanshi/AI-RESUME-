"""Tiny thread-safe TTL cache for single-process CareerLens deployments.

This is deliberately local-memory only: it keeps the portfolio project simple
without Redis, but each server process has its own cache.
"""
from copy import deepcopy
from threading import Lock
from time import monotonic
from typing import Callable, TypeVar


T = TypeVar("T")


class TTLCache:
    def __init__(self) -> None:
        self._entries: dict[str, tuple[float, object]] = {}
        self._lock = Lock()

    def get_or_set(self, key: str, ttl_seconds: int, factory: Callable[[], T]) -> T:
        now = monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry[0] > now:
                return deepcopy(entry[1])  # type: ignore[return-value]

        value = factory()
        with self._lock:
            self._entries[key] = (monotonic() + ttl_seconds, deepcopy(value))
        return value

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._entries.pop(key, None)


dashboard_cache = TTLCache()


def dashboard_cache_key(user_id: int) -> str:
    return f"analysis-dashboard:{user_id}"
