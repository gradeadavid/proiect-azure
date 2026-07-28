"""Qdrant wrapper — collection lifecycle, upsert, similarity search.

The collection is created lazily with the dimension of the first embedding that
arrives. If a later embedding model produces a different dimension, we refuse
loudly: vectors from different models live in different spaces and comparing
them is meaningless — reset the collection and re-ingest instead.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from qdrant_client import QdrantClient, models

from .config import settings


class DimensionMismatch(Exception):
    def __init__(self, existing: int, incoming: int) -> None:
        self.existing = existing
        self.incoming = incoming
        super().__init__(
            f"Collection stores {existing}-dimensional vectors but the current embedding "
            f"model produces {incoming} dimensions. Vectors from different embedding models "
            f"are not comparable — DELETE /collection and re-ingest."
        )


class VectorStore:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url, timeout=10)
        self.collection = settings.qdrant_collection

    # --- lifecycle -----------------------------------------------------------
    def ensure_collection(self, dim: int) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )
            return
        existing = self._vector_size()
        if existing != dim:
            raise DimensionMismatch(existing, dim)

    def reset(self) -> bool:
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
            return True
        return False

    # --- data ----------------------------------------------------------------
    # Fields owned by the pipeline itself — everything else in the payload is
    # caller-supplied metadata (title, product, effective date, ...) and is
    # surfaced back under "metadata" in search() rather than hardcoded here.
    _CORE_KEYS = {"text", "index", "strategy", "source", "ingested_at"}

    def upsert(self, chunks: list[str], vectors: list[list[float]], strategy: str,
               source: str | None, metadata: dict | None = None) -> list[str]:
        source_label = source or "adhoc"
        # Deterministic id (source + chunk index) instead of a random uuid4: re-ingesting
        # the same source overwrites its previous points instead of piling up duplicates.
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_label}:{i}")) for i in range(len(chunks))]
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        meta = metadata or {}
        self.client.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(
                    id=pid,
                    vector=vec,
                    payload={
                        "text": text,
                        "index": i,
                        "strategy": strategy,
                        "source": source_label,
                        "ingested_at": now,
                        **meta,
                    },
                )
                for i, (pid, text, vec) in enumerate(zip(ids, chunks, vectors))
            ],
        )
        return ids

    def search(self, vector: list[float], top_k: int, filters: dict | None = None) -> list[dict]:
        query_filter = None
        if filters:
            query_filter = models.Filter(
                must=[models.FieldCondition(key=k, match=models.MatchValue(value=v))
                      for k, v in filters.items()]
            )
        hits = self.client.query_points(
            collection_name=self.collection, query=vector, limit=top_k, with_payload=True,
            query_filter=query_filter,
        ).points
        results = []
        for h in hits:
            payload = h.payload or {}
            results.append({
                "id": str(h.id),
                "score": round(float(h.score), 4),
                "text": payload.get("text", ""),
                "index": payload.get("index"),
                "strategy": payload.get("strategy"),
                "source": payload.get("source"),
                "metadata": {k: v for k, v in payload.items() if k not in self._CORE_KEYS},
            })
        return results

    # --- introspection --------------------------------------------------------
    def info(self) -> dict:
        if not self.client.collection_exists(self.collection):
            return {"exists": False, "name": self.collection, "points_count": 0,
                    "vector_dimension": None, "distance": None}
        c = self.client.get_collection(self.collection)
        return {
            "exists": True,
            "name": self.collection,
            "points_count": c.points_count or 0,
            "vector_dimension": self._vector_size(),
            "distance": "cosine",
        }

    def ping(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    def _vector_size(self) -> int:
        cfg = self.client.get_collection(self.collection).config.params.vectors
        return cfg.size if hasattr(cfg, "size") else next(iter(cfg.values())).size
