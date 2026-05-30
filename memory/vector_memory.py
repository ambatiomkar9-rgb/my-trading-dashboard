"""Lightweight vector memory with deterministic local embeddings."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VectorRecord:
    """Vector record container."""

    record_id: str
    text: str
    metadata: Dict[str, Any]
    vector: np.ndarray


class VectorMemory:
    """
    In-process vector memory for retrieval support.

    This intentionally avoids external embedding dependencies by using
    a deterministic hash-based embedding for portability.
    """

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension
        self._records: Dict[str, VectorRecord] = {}

    def _embed(self, text: str) -> np.ndarray:
        """Create deterministic dense vector from text."""
        vec = np.zeros(self.dimension, dtype=np.float32)
        tokens = text.lower().split()
        for token in tokens:
            h = hashlib.sha256(token.encode("utf-8")).hexdigest()
            idx = int(h[:8], 16) % self.dimension
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def upsert(self, record_id: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        """Insert or update one vector record."""
        metadata = metadata or {}
        vector = self._embed(text)
        self._records[record_id] = VectorRecord(record_id=record_id, text=text, metadata=metadata, vector=vector)
        logger.debug("Vector record upserted id=%s", record_id)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search memory by cosine similarity."""
        if not self._records:
            return []
        q = self._embed(query)
        scored: List[Dict[str, Any]] = []
        for rec in self._records.values():
            score = float(np.dot(q, rec.vector))
            scored.append(
                {
                    "record_id": rec.record_id,
                    "score": score,
                    "text": rec.text,
                    "metadata": rec.metadata,
                }
            )
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    def all_records(self) -> List[Dict[str, Any]]:
        """Return all records."""
        return [
            {"record_id": r.record_id, "text": r.text, "metadata": r.metadata}
            for r in self._records.values()
        ]
