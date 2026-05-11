"""Health and metrics routes."""

from time import perf_counter

from fastapi import APIRouter

router = APIRouter(tags=["health"])
STARTED_AT = perf_counter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return liveness status."""

    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Return readiness status."""

    return {"status": "ready"}


@router.get("/metrics")
async def metrics() -> dict[str, float | str]:
    """Return lightweight application metrics."""

    return {"service": "rag-api", "uptime_seconds": round(perf_counter() - STARTED_AT, 2)}
