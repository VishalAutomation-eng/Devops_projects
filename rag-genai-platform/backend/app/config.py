"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the RAG API.

    :ivar app_name: Human friendly application name.
    :ivar database_url: Async SQLAlchemy database URL.
    :ivar secret_key: JWT signing secret.
    :ivar algorithm: JWT signing algorithm.
    :ivar ollama_url: Ollama generation endpoint.
    :ivar model: Ollama model name.
    :ivar embedding_service_url: External embedding service base URL.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise RAG Generative AI Platform"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str = Field(default="sqlite+aiosqlite:///./rag_app.db", alias="DATABASE_URL")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        alias="CORS_ORIGINS",
    )

    ollama_url: str = Field(default="http://111.118.189.124:11435/api/generate", alias="OLLAMA_URL")
    model: str = Field(default="gpt-oss:120b", alias="MODEL")
    embedding_service_url: str = Field(
        default="http://111.118.189.124:8050",
        alias="EMBEDDING_SERVICE_URL",
    )
    request_timeout_seconds: float = Field(default=60.0, alias="REQUEST_TIMEOUT_SECONDS")
    llm_retry_count: int = Field(default=3, alias="LLM_RETRY_COUNT")

    upload_dir: Path = Field(default=Path("uploads"), alias="UPLOAD_DIR")
    vector_store_dir: Path = Field(default=Path("vector_store"), alias="VECTOR_STORE_DIR")
    max_upload_mb: int = Field(default=25, alias="MAX_UPLOAD_MB")
    chunk_size: int = Field(default=900, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=5, alias="TOP_K")

    @property
    def allowed_origins(self) -> list[str]:
        """Return configured CORS origins as a list."""

        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    return settings
