"""LRU prompt cache for Ollama API calls — avoids redundant inference on repeated queries."""
from __future__ import annotations

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PromptCache:
    """
    In-memory LRU cache keyed by (model, messages_hash).

    Args:
        max_size: Maximum number of cached responses.
        ttl_sec: Time-to-live in seconds for each entry.
    """

    def __init__(self, max_size: int = 256, ttl_sec: int = 3600) -> None:
        self._max_size = max_size
        self._ttl_sec = ttl_sec
        self._cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _hash_key(model: str, messages: list[dict[str, str]]) -> str:
        """Deterministic hash of model + messages for cache lookup."""
        raw = f"{model}:{str(messages)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

    def get(self, model: str, messages: list[dict[str, str]]) -> Optional[str]:
        """Return cached reply if fresh, else None."""
        key = self._hash_key(model, messages)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        reply, ts = entry
        if time.time() - ts > self._ttl_sec:
            self._cache.pop(key, None)
            self._misses += 1
            return None
        self._cache.move_to_end(key)
        self._hits += 1
        return reply

    def put(self, model: str, messages: list[dict[str, str]], reply: str) -> None:
        """Store a reply in the cache."""
        key = self._hash_key(model, messages)
        self._cache[key] = (reply, time.time())
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 1) if total else 0.0,
            "ttl_sec": self._ttl_sec,
        }

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0


# Global singleton
_prompt_cache = PromptCache()


def get_prompt_cache() -> PromptCache:
    return _prompt_cache
