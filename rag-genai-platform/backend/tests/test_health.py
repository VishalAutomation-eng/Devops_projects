from app.routes.health_routes import health


async def test_health_endpoint() -> None:
    response = await health()
    assert response["status"] == "ok"
