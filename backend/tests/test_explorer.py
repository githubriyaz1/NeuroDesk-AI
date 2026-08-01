import pytest
from httpx import AsyncClient
from fastapi import status
from app.models.asset import AssetStatus


@pytest.mark.asyncio
async def test_bulk_actions_and_archive(async_client: AsyncClient, auth_headers: dict):
    # 1. Upload 3 distinct assets (distinct contents to generate unique SHA256 checksums)
    asset_ids = []
    for i in range(3):
        res = await async_client.post(
            "/api/v1/assets/upload",
            files={"file": (f"test_explorer_{i}.txt", f"Explorer test data content unique {i}".encode(), "text/plain")},
            data={"description": f"Explorer test file {i}"},
            headers=auth_headers,
        )
        assert res.status_code == status.HTTP_201_CREATED
        asset_ids.append(res.json()["id"])

    assert len(set(asset_ids)) == 3

    # 2. Bulk favorite
    bulk_fav_res = await async_client.post(
        "/api/v1/assets/bulk-action",
        json={"asset_ids": asset_ids, "action": "favorite"},
        headers=auth_headers,
    )
    assert bulk_fav_res.status_code == status.HTTP_200_OK
    assert bulk_fav_res.json()["processed_count"] == 3

    # 3. Verify favorites filter
    fav_list = await async_client.get("/api/v1/assets?is_favorite=true", headers=auth_headers)
    assert fav_list.status_code == status.HTTP_200_OK
    fav_items = fav_list.json()["items"]
    assert len(fav_items) >= 3

    # 4. Toggle archive single asset
    archive_res = await async_client.post(
        f"/api/v1/assets/{asset_ids[0]}/archive",
        json={"is_archived": True},
        headers=auth_headers,
    )
    assert archive_res.status_code == status.HTTP_200_OK
    assert archive_res.json()["status"] == AssetStatus.ARCHIVED.value

    # 5. Bulk soft delete remaining 2 assets
    bulk_del_res = await async_client.post(
        "/api/v1/assets/bulk-action",
        json={"asset_ids": asset_ids[1:], "action": "delete"},
        headers=auth_headers,
    )
    assert bulk_del_res.status_code == status.HTTP_200_OK
    assert bulk_del_res.json()["processed_count"] == 2

    # 6. Bulk restore
    bulk_restore_res = await async_client.post(
        "/api/v1/assets/bulk-action",
        json={"asset_ids": asset_ids[1:], "action": "restore"},
        headers=auth_headers,
    )
    assert bulk_restore_res.status_code == status.HTTP_200_OK
    assert bulk_restore_res.json()["processed_count"] == 2
