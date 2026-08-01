import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_blueprint(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Smart Logistics Platform",
        "idea_description": "AI-driven fleet routing and package delivery tracking engine.",
        "target_stack": "React + Python FastAPI + PostgreSQL",
    }
    response = await async_client.post(
        "/api/v1/project-generator/generate", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "architecture_overview" in data
    assert "database_design" in data
    assert "api_plan" in data
    assert "feature_breakdown" in data
    assert "roadmap" in data
