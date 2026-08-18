import pytest
from httpx import AsyncClient
from fastapi import status
from app.services.query_parser import query_parser


def test_query_parser_unit():
    raw = "report invoice type:pdf favorite:true status:ready size>10MB created:this-week"
    res = query_parser.parse(raw)

    assert res["free_text"] == "report invoice"
    assert res["asset_type"] == "REPORT"
    assert res["is_favorite"] is True
    assert res["status"] == "READY"
    assert res["min_size_bytes"] == 10 * 1024 * 1024
    assert res["created_after"] is not None


@pytest.mark.asyncio
async def test_search_and_discovery_pipeline(async_client: AsyncClient, auth_headers: dict):
    # 1. Upload sample CSV file
    csv_bytes = b"id,name,role\n1,Alice,Engineer\n2,Bob,Scientist\n"
    up_res = await async_client.post(
        "/api/v1/assets/upload",
        files={"file": ("search_test_data.csv", csv_bytes, "text/csv")},
        data={"description": "Search Index Test File"},
        headers=auth_headers,
    )
    assert up_res.status_code == status.HTTP_201_CREATED
    asset_id = up_res.json()["id"]

    # 2. GET /api/v1/search with query text
    search_res = await async_client.get(
        "/api/v1/search",
        params={"q": "search_test type:csv"},
        headers=auth_headers,
    )
    assert search_res.status_code == status.HTTP_200_OK
    data = search_res.json()
    assert data["total"] > 0
    assert len(data["items"]) > 0
    assert data["items"][0]["asset"]["id"] == asset_id

    # 3. GET /api/v1/search/suggestions
    sug_res = await async_client.get(
        "/api/v1/search/suggestions",
        params={"q": "search_test"},
        headers=auth_headers,
    )
    assert sug_res.status_code == status.HTTP_200_OK
    sug_data = sug_res.json()
    assert len(sug_data["suggestions"]) > 0

    # 4. GET Discovery endpoints
    for endpoint in ["recent", "favorites", "largest", "newest"]:
        disc_res = await async_client.get(
            f"/api/v1/discovery/{endpoint}",
            headers=auth_headers,
        )
        assert disc_res.status_code == status.HTTP_200_OK
        assert isinstance(disc_res.json(), list)


@pytest.mark.asyncio
async def test_search_unauthorized(async_client: AsyncClient):
    res = await async_client.get("/api/v1/search?q=test")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
