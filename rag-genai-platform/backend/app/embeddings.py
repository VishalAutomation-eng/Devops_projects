"""External embedding service client with in-memory caching."""

import hashlib
from collections import OrderedDict
from typing import Any

import httpx

from app.config import Settings
from app.utils.logger import get_logger


class EmbeddingService:
    """Client for creating text embeddings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize HTTP client settings and cache."""

        self.settings = settings
        self.cache: OrderedDict[str, list[float]] = OrderedDict()
        self.cache_limit = 4096
        self.logger = get_logger("embeddings")

    async def embed(self, text: str) -> list[float]:
        """Generate one embedding vector for text."""

        return (await self.embed_many([text]))[0]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts.

        The method supports common embedding service response shapes:
        ``{"embedding": [...]}``, ``{"embeddings": [[...]]}``, and
        ``{"data": [{"embedding": [...]}]}``.
        """

        results: list[list[float] | None] = []
        misses: list[str] = []
        for text in texts:
            key = self._cache_key(text)
            cached = self.cache.get(key)
            if cached is None:
                results.append(None)
                misses.append(text)
            else:
                self.cache.move_to_end(key)
                results.append(cached)

        if misses:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(
                    f"{self.settings.embedding_service_url.rstrip('/')}/embed",
                    json={"texts": misses},
                )
                if response.status_code == 404:
                    response = await client.post(
                        f"{self.settings.embedding_service_url.rstrip('/')}/embeddings",
                        json={"input": misses},
                    )
                response.raise_for_status()
            vectors = self._parse_response(response.json(), len(misses))
            for text, vector in zip(misses, vectors, strict=True):
                self._store_cache(text, vector)

            iterator = iter(vectors)
            results = [next(iterator) if item is None else item for item in results]

        final = [item for item in results if item is not None]
        self.logger.info("embeddings_generated", requested=len(texts), cache_misses=len(misses))
        return final

    def _parse_response(self, payload: dict[str, Any], expected: int) -> list[list[float]]:
        """Parse embeddings from a flexible JSON payload."""

        if "embeddings" in payload:
            vectors = payload["embeddings"]
        elif "embedding" in payload:
            vectors = [payload["embedding"]]
        elif "data" in payload:
            vectors = [item["embedding"] for item in payload["data"]]
        else:
            raise ValueError("Embedding service response did not include embeddings")
        if len(vectors) != expected:
            raise ValueError("Embedding service returned an unexpected vector count")
        return [[float(value) for value in vector] for vector in vectors]

    def _store_cache(self, text: str, vector: list[float]) -> None:
        """Store vector in bounded LRU cache."""

        self.cache[self._cache_key(text)] = vector
        self.cache.move_to_end(self._cache_key(text))
        if len(self.cache) > self.cache_limit:
            self.cache.popitem(last=False)

    @staticmethod
    def _cache_key(text: str) -> str:
        """Return a stable cache key for text."""

        return hashlib.sha256(text.encode("utf-8")).hexdigest()
