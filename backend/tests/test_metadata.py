import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_metadata_extraction_csv_and_refresh(async_client: AsyncClient, auth_headers: dict):
    # 1. Upload CSV file
    csv_content = b"header_1,header_2,header_3\nval1,100,true\nval2,200,false\n"
    res = await async_client.post(
        "/api/v1/assets/upload",
        files={"file": ("telemetry_data.csv", csv_content, "text/csv")},
        data={"description": "CSV Telemetry Test File"},
        headers=auth_headers,
    )
    assert res.status_code == status.HTTP_201_CREATED
    asset_id = res.json()["id"]

    # 2. GET /api/v1/assets/{asset_id}/metadata
    meta_res = await async_client.get(f"/api/v1/assets/{asset_id}/metadata", headers=auth_headers)
    assert meta_res.status_code == status.HTTP_200_OK
    data = meta_res.json()

    assert data["asset_id"] == asset_id
    assert data["total_keys"] > 0
    assert len(data["groups"]) > 0

    # Verify extracted CSV metadata fields
    items_map = {item["key"]: item["value"] for item in data["items"]}
    assert "row_count" in items_map
    assert "column_count" in items_map
    assert "mime_type" in items_map
    assert "csv" in items_map["mime_type"].lower() or "excel" in items_map["mime_type"].lower()

    # 3. POST /api/v1/assets/{asset_id}/metadata/refresh
    refresh_res = await async_client.post(f"/api/v1/assets/{asset_id}/metadata/refresh", headers=auth_headers)
    assert refresh_res.status_code == status.HTTP_200_OK
    refresh_data = refresh_res.json()
    assert refresh_data["total_keys"] > 0


@pytest.mark.asyncio
async def test_metadata_unauthorized_and_not_found(async_client: AsyncClient, auth_headers: dict):
    fake_uuid = "00000000-0000-0000-0000-000000000000"

    # Unauthenticated call
    unauth_res = await async_client.get(f"/api/v1/assets/{fake_uuid}/metadata")
    assert unauth_res.status_code == status.HTTP_401_UNAUTHORIZED

    # Missing asset call
    not_found_res = await async_client.get(f"/api/v1/assets/{fake_uuid}/metadata", headers=auth_headers)
    assert not_found_res.status_code == status.HTTP_404_NOT_FOUND
