import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workspace_items(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.get("/api/v1/workspace", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_create_workspace_item(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "name": "Test Analytics Dataset",
        "description": "Dataset for automated test suite",
        "file_type": "csv",
    }
    response = await async_client.post("/api/v1/workspace", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["status"] == "created"
