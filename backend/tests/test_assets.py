import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_asset_success(async_client: AsyncClient, auth_headers: dict):
    file_content = b"user_id,amount,score\n1,100.50,0.95\n2,250.00,0.88\n"
    files = {"file": ("test_dataset.csv", io.BytesIO(file_content), "text/csv")}
    data = {"description": "Customer transactional telemetry data"}

    response = await async_client.post(
        "/api/v1/assets/upload", headers=auth_headers, files=files, data=data
    )
    assert response.status_code == 201
    asset = response.json()
    assert asset["original_filename"] == "test_dataset.csv"
    assert asset["asset_type"] == "SPREADSHEET"
    assert asset["file_size"] == len(file_content)
    assert asset["status"] == "READY"
    assert "storage_path" not in asset  # Never expose internal storage path to client


@pytest.mark.asyncio
async def test_upload_empty_file_fails(async_client: AsyncClient, auth_headers: dict):
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    res = await async_client.post("/api/v1/assets/upload", headers=auth_headers, files=files)
    assert res.status_code == 400
    msg = res.json().get("message") or res.json().get("detail")
    assert "Empty files" in msg


@pytest.mark.asyncio
async def test_upload_invalid_extension_fails(async_client: AsyncClient, auth_headers: dict):
    files = {"file": ("script.exe", io.BytesIO(b"binary content"), "application/octet-stream")}
    res = await async_client.post("/api/v1/assets/upload", headers=auth_headers, files=files)
    assert res.status_code == 400
    msg = res.json().get("message") or res.json().get("detail")
    assert "Unsupported file extension" in msg


@pytest.mark.asyncio
async def test_download_asset_success(async_client: AsyncClient, auth_headers: dict):
    file_content = b"Hello NeuroDesk DAMS storage system!"
    files = {"file": ("notes.txt", io.BytesIO(file_content), "text/plain")}

    upload_res = await async_client.post(
        "/api/v1/assets/upload", headers=auth_headers, files=files
    )
    assert upload_res.status_code == 201
    asset_id = upload_res.json()["id"]

    download_res = await async_client.get(
        f"/api/v1/assets/{asset_id}/download", headers=auth_headers
    )
    assert download_res.status_code == 200
    assert download_res.content == file_content


@pytest.mark.asyncio
async def test_list_and_filter_assets(async_client: AsyncClient, auth_headers: dict):
    file_content = b"Image sample data bytes"
    files = {"file": ("banner.png", io.BytesIO(file_content), "image/png")}
    await async_client.post("/api/v1/assets/upload", headers=auth_headers, files=files)

    res = await async_client.get("/api/v1/assets", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert "items" in body
    assert body["page"] == 1


@pytest.mark.asyncio
async def test_rename_and_favorite_asset(async_client: AsyncClient, auth_headers: dict):
    files = {"file": ("report_draft.pdf", io.BytesIO(b"PDF header"), "application/pdf")}
    up = await async_client.post("/api/v1/assets/upload", headers=auth_headers, files=files)
    asset_id = up.json()["id"]

    # Rename
    patch_res = await async_client.patch(
        f"/api/v1/assets/{asset_id}",
        headers=auth_headers,
        json={"name": "Final Approved Q3 Report", "description": "Updated description"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Final Approved Q3 Report"

    # Favorite
    fav_res = await async_client.post(
        f"/api/v1/assets/{asset_id}/favorite",
        headers=auth_headers,
        json={"is_favorite": True},
    )
    assert fav_res.status_code == 200
    assert fav_res.json()["is_favorite"] is True


@pytest.mark.asyncio
async def test_soft_delete_and_restore_asset(async_client: AsyncClient, auth_headers: dict):
    files = {"file": ("temp.log", io.BytesIO(b"log data"), "text/plain")}
    up = await async_client.post("/api/v1/assets/upload", headers=auth_headers, files=files)
    assert up.status_code == 201
    asset_id = up.json()["id"]

    # Delete
    del_res = await async_client.delete(f"/api/v1/assets/{asset_id}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["is_deleted"] is True
    assert del_res.json()["status"] == "DELETED"

    # Attempt download of deleted asset should return 404
    down_res = await async_client.get(f"/api/v1/assets/{asset_id}/download", headers=auth_headers)
    assert down_res.status_code == 404

    # Restore
    res_res = await async_client.post(f"/api/v1/assets/{asset_id}/restore", headers=auth_headers)
    assert res_res.status_code == 200
    assert res_res.json()["is_deleted"] is False
    assert res_res.json()["status"] == "READY"


@pytest.mark.asyncio
async def test_asset_statistics(async_client: AsyncClient, auth_headers: dict):
    files = {"file": ("model.onnx", io.BytesIO(b"onnx binary"), "application/octet-stream")}
    await async_client.post("/api/v1/assets/upload", headers=auth_headers, files=files)

    stats_res = await async_client.get("/api/v1/assets/statistics", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_assets"] >= 1
    assert stats["total_storage_used_bytes"] > 0
    assert stats["total_storage_bytes"] > 0


@pytest.mark.asyncio
async def test_asset_unauthorized_access(async_client: AsyncClient):
    files = {"file": ("unauthorized.txt", io.BytesIO(b"data"), "text/plain")}
    res = await async_client.post("/api/v1/assets/upload", files=files)
    assert res.status_code == 401
