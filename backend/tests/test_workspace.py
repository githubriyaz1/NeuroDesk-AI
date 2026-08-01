import pytest
from httpx import AsyncClient


async def get_authenticated_headers(async_client: AsyncClient) -> dict:
    email = "ws_tester@neurodesk.ai"
    password = "TestPassword2026!"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Workspace Tester", "password": password},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_workspace_items(async_client: AsyncClient):
    headers = await get_authenticated_headers(async_client)
    response = await async_client.get("/api/v1/workspace", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_create_workspace_item(async_client: AsyncClient):
    headers = await get_authenticated_headers(async_client)
    payload = {
        "name": "Test Analytics Dataset",
        "description": "Dataset for automated test suite",
        "file_type": "csv",
    }
    response = await async_client.post("/api/v1/workspace", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["status"] == "created"
