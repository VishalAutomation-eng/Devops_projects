"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.routes import auth_routes, health_routes, rag_routes
from app.utils.logger import RequestLoggingMiddleware, configure_logging, get_logger

configure_logging()
settings = get_settings()
logger = get_logger("app")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Production-grade RAG application with JWT auth, FAISS retrieval, "
        "and Ollama generation."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(health_routes.router)
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(rag_routes.router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize database and runtime directories."""

    await init_db()
    logger.info("application_started", environment=settings.environment)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return a consistent response for unexpected exceptions."""

    logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
