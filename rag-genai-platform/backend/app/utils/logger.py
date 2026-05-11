"""Structured logging utilities."""

import logging
import sys
from collections.abc import Callable
from time import perf_counter

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def configure_logging() -> None:
    """Configure JSON logging for application and access logs."""

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named structured logger.

    :param name: Logger name.
    :return: Bound structlog logger.
    """

    return structlog.get_logger(name)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that records request latency and response status."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request lifecycle data.

        :param request: Incoming HTTP request.
        :param call_next: Next ASGI handler.
        :return: HTTP response.
        """

        started = perf_counter()
        logger = get_logger("request")
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed", path=request.url.path, method=request.method)
            raise
        elapsed_ms = round((perf_counter() - started) * 1000, 2)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
        )
        return response
