"""FAISS vector store abstraction."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import faiss
import numpy as np

from app.config import Settings


@dataclass(slots=True)
class ChunkMetadata:
    """Metadata attached to each vector."""

    document_id: int
    filename: str
    page: int
    text: str


@dataclass(slots=True)
class SearchResult:
    """Vector search result."""

    metadata: ChunkMetadata
    score: float


class VectorStore:
    """Persistent per-user FAISS vector store."""

    def __init__(self, settings: Settings) -> None:
        """Initialize vector store paths."""

        self.settings = settings

    def add_vectors(
        self,
        user_id: int,
        vectors: list[list[float]],
        metadatas: list[ChunkMetadata],
    ) -> None:
        """Append vectors and metadata for a user."""

        if not vectors:
            return
        user_dir = self._user_dir(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        matrix = self._normalize(np.array(vectors, dtype="float32"))
        index = self._load_index(user_id, dimension=matrix.shape[1])
        index.add(matrix)

        metadata = self._load_metadata(user_id)
        metadata.extend(asdict(item) for item in metadatas)
        faiss.write_index(index, str(self._index_path(user_id)))
        self._metadata_path(user_id).write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def search(self, user_id: int, query_vector: list[float], top_k: int) -> list[SearchResult]:
        """Search the user index by cosine similarity."""

        index_path = self._index_path(user_id)
        if not index_path.exists():
            return []
        index = faiss.read_index(str(index_path))
        metadata = self._load_metadata(user_id)
        query = self._normalize(np.array([query_vector], dtype="float32"))
        scores, indices = index.search(query, top_k)
        results: list[SearchResult] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0 or idx >= len(metadata):
                continue
            results.append(
                SearchResult(
                    metadata=ChunkMetadata(**metadata[idx]),
                    score=float(score),
                )
            )
        return results

    def _load_index(self, user_id: int, dimension: int) -> faiss.Index:
        """Load or create a FAISS inner-product index."""

        index_path = self._index_path(user_id)
        if index_path.exists():
            return faiss.read_index(str(index_path))
        return faiss.IndexFlatIP(dimension)

    def _load_metadata(self, user_id: int) -> list[dict]:
        """Load chunk metadata from disk."""

        path = self._metadata_path(user_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _user_dir(self, user_id: int) -> Path:
        """Return the vector store directory for a user."""

        return self.settings.vector_store_dir / str(user_id)

    def _index_path(self, user_id: int) -> Path:
        """Return the FAISS index path for a user."""

        return self._user_dir(user_id) / "index.faiss"

    def _metadata_path(self, user_id: int) -> Path:
        """Return metadata path for a user."""

        return self._user_dir(user_id) / "metadata.json"

    @staticmethod
    def _normalize(matrix: np.ndarray) -> np.ndarray:
        """L2 normalize vectors for cosine similarity."""

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return matrix / norms
