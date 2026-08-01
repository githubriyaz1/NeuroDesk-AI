import io
import pytest
from httpx import AsyncClient
from PIL import Image
import openpyxl


@pytest.mark.asyncio
async def test_csv_preview_success(async_client: AsyncClient, auth_headers: dict):
    csv_bytes = b"id,name,role,salary\n101,Alice,Data Engineer,120000\n102,Bob,AI Scientist,140000\n"
    files = {"file": ("employees.csv", io.BytesIO(csv_bytes), "text/csv")}

    upload_res = await async_client.post(
        "/api/v1/assets/upload", headers=auth_headers, files=files
    )
    assert upload_res.status_code == 201
    asset_id = upload_res.json()["id"]

    # Preview content payload
    prev_res = await async_client.get(
        f"/api/v1/assets/{asset_id}/preview", headers=auth_headers
    )
    assert prev_res.status_code == 200
    prev = prev_res.json()
    assert prev["preview_type"] == "CSV"
    assert prev["can_preview"] is True
    assert prev["content"]["columns"] == ["id", "name", "role", "salary"]
    assert len(prev["content"]["rows"]) == 2
    assert prev["content"]["rows"][0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_excel_preview_success(async_client: AsyncClient, auth_headers: dict):
    # Create in-memory XLSX workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Financial Metrics"
    ws.append(["Quarter", "Revenue", "Margin"])
    ws.append(["Q1", 500000, "22%"])
    ws.append(["Q2", 650000, "25%"])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    files = {"file": ("financials.xlsx", output, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    up_res = await async_client.post(
        "/api/v1/assets/upload", headers=auth_headers, files=files
    )
    assert up_res.status_code == 201
    asset_id = up_res.json()["id"]

    prev_res = await async_client.get(
        f"/api/v1/assets/{asset_id}/preview", headers=auth_headers
    )
    assert prev_res.status_code == 200
    prev = prev_res.json()
    assert prev["preview_type"] == "EXCEL"
    assert "Financial Metrics" in prev["content"]["sheet_names"]
    assert prev["content"]["sheets"]["Financial Metrics"]["headers"] == ["Quarter", "Revenue", "Margin"]


@pytest.mark.asyncio
async def test_image_preview_success(async_client: AsyncClient, auth_headers: dict):
    # Create in-memory PNG image
    img = Image.new("RGB", (320, 240), color="indigo")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    files = {"file": ("logo.png", img_bytes, "image/png")}
    up_res = await async_client.post(
        "/api/v1/assets/upload", headers=auth_headers, files=files
    )
    assert up_res.status_code == 201
    asset_id = up_res.json()["id"]

    # Preview content payload
    prev_res = await async_client.get(
        f"/api/v1/assets/{asset_id}/preview", headers=auth_headers
    )
    assert prev_res.status_code == 200
    prev = prev_res.json()
    assert prev["preview_type"] == "IMAGE"
    assert prev["metadata"]["width"] == 320
    assert prev["metadata"]["height"] == 240

    # Thumbnail endpoint
    thumb_res = await async_client.get(
        f"/api/v1/assets/{asset_id}/thumbnail", headers=auth_headers
    )
    assert thumb_res.status_code == 200
    assert thumb_res.headers["content-type"] == "image/png"


@pytest.mark.asyncio
async def test_unsupported_file_preview(async_client: AsyncClient, auth_headers: dict):
    files = {"file": ("weights.bin", io.BytesIO(b"0101010101"), "application/octet-stream")}
    up_res = await async_client.post(
        "/api/v1/assets/upload", headers=auth_headers, files=files
    )
    assert up_res.status_code == 201
    asset_id = up_res.json()["id"]

    prev_res = await async_client.get(
        f"/api/v1/assets/{asset_id}/preview", headers=auth_headers
    )
    assert prev_res.status_code == 200
    prev = prev_res.json()
    assert prev["preview_type"] == "UNSUPPORTED"
    assert prev["can_preview"] is False


@pytest.mark.asyncio
async def test_preview_missing_asset_fails(async_client: AsyncClient, auth_headers: dict):
    res = await async_client.get(
        "/api/v1/assets/00000000-0000-0000-0000-000000000000/preview", headers=auth_headers
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_preview_unauthorized_fails(async_client: AsyncClient):
    res = await async_client.get(
        "/api/v1/assets/00000000-0000-0000-0000-000000000000/preview"
    )
    assert res.status_code == 401
