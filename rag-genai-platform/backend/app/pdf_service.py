"""PDF validation, storage, and extraction services."""

import re
import uuid
from pathlib import Path

import pdfplumber
from fastapi import UploadFile

from app.config import Settings


class PDFService:
    """Service for secure PDF uploads and text extraction."""

    def __init__(self, settings: Settings) -> None:
        """Initialize service with application settings."""

        self.settings = settings

    async def save_pdf(self, user_id: int, file: UploadFile) -> Path:
        """Validate and persist an uploaded PDF.

        :raises ValueError: If the file is invalid or too large.
        """

        if file.content_type not in {"application/pdf", "application/x-pdf"}:
            raise ValueError("Only PDF files are supported")

        content = await file.read()
        max_bytes = self.settings.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise ValueError(f"PDF exceeds {self.settings.max_upload_mb} MB limit")
        if not content.startswith(b"%PDF"):
            raise ValueError("Uploaded file is not a valid PDF")

        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", file.filename or "document.pdf")
        user_dir = self.settings.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        destination = user_dir / f"{uuid.uuid4()}_{safe_name}"
        destination.write_bytes(content)
        return destination

    async def extract_text_by_page(self, path: Path) -> list[tuple[int, str]]:
        """Extract text from each PDF page.

        :param path: Path to a stored PDF file.
        :return: Tuples of page number and extracted text.
        """

        pages: list[tuple[int, str]] = []
        with pdfplumber.open(path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append((page_number, text))
        return pages
