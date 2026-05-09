from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from uuid import UUID

from app.core.config import get_settings


@dataclass(frozen=True)
class VectorSearchHit:
    id: str
    distance: float


def embed_text(text: str, dimensions: int = 64) -> list[float]:
    vector = [0.0] * dimensions
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % dimensions
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


class ChromaLogStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _collection(self):
        import chromadb

        client = chromadb.HttpClient(host=self.settings.chroma_host, port=self.settings.chroma_port)
        return client.get_or_create_collection(
            name=self.settings.chroma_collection,
            metadata={"description": "AI DevOps semantic log index"},
        )

    async def upsert_log(
        self,
        log_id: UUID,
        organization_id: UUID,
        document: str,
        metadata: dict,
    ) -> bool:
        try:
            collection = self._collection()
            collection.upsert(
                ids=[str(log_id)],
                documents=[document],
                embeddings=[embed_text(document)],
                metadatas=[
                    {
                        "organization_id": str(organization_id),
                        **{key: value for key, value in metadata.items() if value is not None},
                    }
                ],
            )
            return True
        except Exception:
            return False

    async def search(self, organization_id: UUID, query: str, limit: int) -> list[VectorSearchHit]:
        try:
            collection = self._collection()
            result = collection.query(
                query_embeddings=[embed_text(query)],
                n_results=limit,
                where={"organization_id": str(organization_id)},
                include=["distances"],
            )
            ids = result.get("ids", [[]])[0]
            distances = result.get("distances", [[]])[0]
            return [
                VectorSearchHit(id=log_id, distance=float(distance))
                for log_id, distance in zip(ids, distances, strict=False)
            ]
        except Exception:
            return []

