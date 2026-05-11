"""End-to-end RAG orchestration."""

import re
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.embeddings import EmbeddingService
from app.llm_service import LLMService
from app.models import Document
from app.pdf_service import PDFService
from app.schemas import AnswerResponse, SourceChunk
from app.utils.logger import get_logger
from app.vector_store import ChunkMetadata, VectorStore


class RAGPipeline:
    """Coordinates ingestion, retrieval, and generation."""

    def __init__(
        self,
        settings: Settings,
        pdf_service: PDFService,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        llm_service: LLMService,
    ) -> None:
        """Initialize the pipeline with its collaborators."""

        self.settings = settings
        self.pdf_service = pdf_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.logger = get_logger("rag")

    async def ingest_pdf(
        self,
        db: AsyncSession,
        user_id: int,
        filename: str,
        path: Path,
    ) -> Document:
        """Extract, chunk, embed, and index a PDF."""

        pages = await self.pdf_service.extract_text_by_page(path)
        document = Document(
            owner_id=user_id,
            filename=filename,
            storage_path=str(path),
            chunk_count=0,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        chunks = self._chunk_pages(pages)
        texts = [chunk["text"] for chunk in chunks]
        vectors = await self.embedding_service.embed_many(texts) if texts else []
        metadatas = [
            ChunkMetadata(
                document_id=document.id,
                filename=filename,
                page=int(chunk["page"]),
                text=str(chunk["text"]),
            )
            for chunk in chunks
        ]
        self.vector_store.add_vectors(user_id, vectors, metadatas)
        document.chunk_count = len(chunks)
        await db.commit()
        await db.refresh(document)
        self.logger.info(
            "document_ingested",
            user_id=user_id,
            document_id=document.id,
            chunks=len(chunks),
        )
        return document

    async def answer(self, user_id: int, question: str, top_k: int | None = None) -> AnswerResponse:
        """Retrieve context and generate a contextual answer."""

        query_vector = await self.embedding_service.embed(question)
        results = self.vector_store.search(user_id, query_vector, top_k or self.settings.top_k)
        if not results:
            return AnswerResponse(
                answer=(
                    "I could not find indexed document context for this question. "
                    "Upload a PDF first."
                ),
                sources=[],
                token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            )
        context = "\n\n".join(
            (
                f"[Source {index}: {result.metadata.filename}, "
                f"page {result.metadata.page}]\n{result.metadata.text}"
            )
            for index, result in enumerate(results, start=1)
        )
        prompt = self._build_prompt(question, context)
        self.logger.info(
            "retrieval_completed",
            user_id=user_id,
            top_k=len(results),
            scores=[round(item.score, 4) for item in results],
        )
        self.logger.info("prompt_rendered", user_id=user_id, prompt_chars=len(prompt))
        answer, usage = await self.llm_service.generate(prompt)
        return AnswerResponse(
            answer=answer,
            sources=[
                SourceChunk(
                    document_id=item.metadata.document_id,
                    filename=item.metadata.filename,
                    page=item.metadata.page,
                    score=item.score,
                    text=item.metadata.text[:600],
                )
                for item in results
            ],
            token_usage=usage,
        )

    def _chunk_pages(self, pages: list[tuple[int, str]]) -> list[dict[str, str | int]]:
        """Split page text into overlapping chunks."""

        chunks: list[dict[str, str | int]] = []
        for page, text in pages:
            normalized = re.sub(r"\s+", " ", text).strip()
            start = 0
            while start < len(normalized):
                end = min(start + self.settings.chunk_size, len(normalized))
                boundary = normalized.rfind(". ", start, end)
                if boundary > start + self.settings.chunk_size * 0.55:
                    end = boundary + 1
                chunk = normalized[start:end].strip()
                if chunk:
                    chunks.append({"page": page, "text": chunk})
                if end >= len(normalized):
                    break
                start = max(end - self.settings.chunk_overlap, 0)
        return chunks

    @staticmethod
    def _build_prompt(question: str, context: str) -> str:
        """Render the RAG prompt."""

        return (
            "You are an enterprise knowledge assistant. Answer only from the provided context. "
            "If the answer is not present, say you do not know. Cite source numbers inline.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        )
