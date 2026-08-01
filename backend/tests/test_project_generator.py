import pytest
from httpx import AsyncClient


async def get_authenticated_headers(async_client: AsyncClient) -> dict:
    email = "gen_tester@neurodesk.ai"
    password = "TestPassword2026!"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Generator Tester", "password": password},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_generate_blueprint(async_client: AsyncClient):
    headers = await get_authenticated_headers(async_client)
    payload = {
        "title": "Smart Logistics Platform",
        "idea_description": "AI-driven fleet routing and package delivery tracking engine.",
        "target_stack": "React + Python FastAPI + PostgreSQL",
    }
    response = await async_client.post("/api/v1/project-generator/generate", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "architecture_overview" in data
    assert "database_design" in data
    assert "api_plan" in data
    assert "feature_breakdown" in data
    assert "roadmap" in data
