"""RAG document and question routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.embeddings import EmbeddingService
from app.llm_service import LLMService
from app.models import Document, User
from app.pdf_service import PDFService
from app.rag_pipeline import RAGPipeline
from app.schemas import AnswerResponse, DocumentRead, QuestionRequest
from app.vector_store import VectorStore

router = APIRouter(prefix="/rag", tags=["rag"])


def get_pipeline() -> RAGPipeline:
    """Build pipeline dependencies."""

    settings = get_settings()
    return RAGPipeline(
        settings=settings,
        pdf_service=PDFService(settings),
        embedding_service=EmbeddingService(settings),
        vector_store=VectorStore(settings),
        llm_service=LLMService(settings),
    )


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> DocumentRead:
    """Upload and index a PDF for the authenticated user."""

    try:
        path = await pipeline.pdf_service.save_pdf(current_user.id, file)
        return await pipeline.ingest_pdf(db, current_user.id, file.filename or path.name, path)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/documents", response_model=list[DocumentRead])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentRead]:
    """List documents uploaded by the authenticated user."""

    query = (
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    result = await db.scalars(query)
    return list(result.all())


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    payload: QuestionRequest,
    current_user: User = Depends(get_current_user),
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> AnswerResponse:
    """Answer a question using indexed PDF context."""

    return await pipeline.answer(current_user.id, payload.question, payload.top_k)
