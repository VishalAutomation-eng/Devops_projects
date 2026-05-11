"""Ollama LLM client with retry and timeout handling."""

import asyncio
from typing import Any

import httpx

from app.config import Settings
from app.utils.logger import get_logger


class LLMService:
    """Service for prompt execution against Ollama."""

    def __init__(self, settings: Settings) -> None:
        """Initialize service settings."""

        self.settings = settings
        self.logger = get_logger("llm")

    async def generate(self, prompt: str) -> tuple[str, dict[str, int]]:
        """Generate an answer from the configured Ollama model.

        :param prompt: Fully rendered prompt.
        :return: Generated text and token usage metadata.
        """

        payload = {"model": self.settings.model, "prompt": prompt, "stream": False}
        last_error: Exception | None = None
        for attempt in range(1, self.settings.llm_retry_count + 1):
            try:
                timeout = self.settings.request_timeout_seconds
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(self.settings.ollama_url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    answer = str(data.get("response") or data.get("answer") or "")
                    usage = self._usage(data, prompt, answer)
                    self.logger.info("llm_response", model=self.settings.model, usage=usage)
                    return answer.strip(), usage
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                self.logger.warning("llm_attempt_failed", attempt=attempt, error=str(exc))
                await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError("LLM service failed after retries") from last_error

    @staticmethod
    def _usage(data: dict[str, Any], prompt: str, answer: str) -> dict[str, int]:
        """Extract or estimate token usage from model response."""

        prompt_tokens = int(data.get("prompt_eval_count") or len(prompt.split()))
        completion_tokens = int(data.get("eval_count") or len(answer.split()))
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
