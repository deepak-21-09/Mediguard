"""
Hindsight Memory Engine
-----------------------
Persistent AI memory for MedAgent.

When Qdrant is available (QDRANT_ENABLED=true), memories are embedded and
stored in the vector DB so MedAgent can recall anything across sessions.

When Qdrant is unavailable (default for local dev), falls back to a simple
in-process list that still works for the session.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from core.config import settings


class InMemoryFallback:
    """Simple in-process store used when Qdrant is not available."""

    def __init__(self):
        self._store: list[dict] = []

    async def store(self, user_id: str, memory_type: str, content: str, metadata: dict | None = None) -> str:
        point_id = str(uuid.uuid4())
        self._store.append({
            "id": point_id,
            "user_id": user_id,
            "memory_type": memory_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
        return point_id

    async def recall(self, user_id: str, query: str, memory_types: list[str] | None = None, top_k: int = 10) -> list[dict]:
        results = [m for m in self._store if m["user_id"] == user_id]
        if memory_types:
            results = [m for m in results if m["memory_type"] in memory_types]
        # Simple keyword match as fallback (no embeddings)
        if query:
            scored = []
            q_lower = query.lower()
            for m in results:
                score = sum(1 for word in q_lower.split() if word in m["content"].lower())
                scored.append((score, m))
            scored.sort(key=lambda x: x[0], reverse=True)
            results = [m for _, m in scored[:top_k]]
        return results[-top_k:]

    async def recall_all_by_type(self, user_id: str, memory_type: str, limit: int = 100) -> list[dict]:
        return [m for m in self._store if m["user_id"] == user_id and m["memory_type"] == memory_type][:limit]

    async def delete_memory(self, point_id: str):
        self._store = [m for m in self._store if m["id"] != point_id]


class QdrantMemory:
    """Full vector-backed memory using Qdrant."""

    VECTOR_SIZE = 1536

    def __init__(self):
        from langchain_openai import OpenAIEmbeddings
        from qdrant_client import AsyncQdrantClient
        self.client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)
        self._collection = settings.QDRANT_COLLECTION

    async def _ensure_collection(self):
        from qdrant_client.models import Distance, VectorParams
        collections = await self.client.get_collections()
        names = [c.name for c in collections.collections]
        if self._collection not in names:
            await self.client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=self.VECTOR_SIZE, distance=Distance.COSINE),
            )

    async def store(self, user_id: str, memory_type: str, content: str, metadata: dict | None = None) -> str:
        from qdrant_client.models import PointStruct
        await self._ensure_collection()
        vector = await self.embeddings.aembed_query(content)
        point_id = str(uuid.uuid4())
        await self.client.upsert(
            collection_name=self._collection,
            points=[PointStruct(id=point_id, vector=vector, payload={
                "user_id": user_id, "memory_type": memory_type,
                "content": content, "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat(),
            })],
        )
        return point_id

    async def recall(self, user_id: str, query: str, memory_types: list[str] | None = None, top_k: int = 10) -> list[dict]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        await self._ensure_collection()
        vector = await self.embeddings.aembed_query(query)
        must = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if memory_types:
            must.append(FieldCondition(key="memory_type", match=MatchValue(value=memory_types[0])))
        results = await self.client.search(
            collection_name=self._collection,
            query_vector=vector,
            query_filter=Filter(must=must),
            limit=top_k,
            with_payload=True,
        )
        return [{"id": h.id, "score": h.score, **h.payload} for h in results]

    async def recall_all_by_type(self, user_id: str, memory_type: str, limit: int = 100) -> list[dict]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        await self._ensure_collection()
        results, _ = await self.client.scroll(
            collection_name=self._collection,
            scroll_filter=Filter(must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="memory_type", match=MatchValue(value=memory_type)),
            ]),
            limit=limit, with_payload=True,
        )
        return [{"id": p.id, **p.payload} for p in results]

    async def delete_memory(self, point_id: str):
        await self.client.delete(collection_name=self._collection, points_selector=[point_id])


# Expose unified type
HindsightMemory = QdrantMemory | InMemoryFallback

_memory_instance = None


def get_memory():
    global _memory_instance
    if _memory_instance is None:
        if settings.QDRANT_ENABLED:
            try:
                _memory_instance = QdrantMemory()
                print("[Hindsight] Using Qdrant vector memory.")
            except Exception as e:
                print(f"[Hindsight] Qdrant unavailable ({e}), using in-memory fallback.")
                _memory_instance = InMemoryFallback()
        else:
            print("[Hindsight] Using in-memory fallback (set QDRANT_ENABLED=true to use Qdrant).")
            _memory_instance = InMemoryFallback()
    return _memory_instance
