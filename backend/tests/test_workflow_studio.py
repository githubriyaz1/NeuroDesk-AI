import pytest
from httpx import AsyncClient
from fastapi import status

from app.core.workflow.data_transform import data_transform_evaluator
from app.core.workflow.http_executor import http_executor
from app.core.workflow.python_sandbox import python_sandbox


@pytest.mark.asyncio
async def test_python_sandbox_security_rejection():
    """Verifies that forbidden imports, system calls, and unsafe attributes are rejected by AST security auditing."""
    # Forbidden import
    res1 = await python_sandbox.execute_script("import os; result = os.getcwd()")
    assert res1["success"] is False
    assert "Security Policy Violation" in res1["stderr"]

    # Forbidden call eval
    res2 = await python_sandbox.execute_script("result = eval('2 + 2')")
    assert res2["success"] is False
    assert "Security Policy Violation" in res2["stderr"]

    # Forbidden attribute __builtins__
    res3 = await python_sandbox.execute_script("result = __builtins__")
    assert res3["success"] is False
    assert "Security Policy Violation" in res3["stderr"]


@pytest.mark.asyncio
async def test_python_sandbox_safe_execution():
    """Verifies that safe mathematical and data transformations execute correctly with outputs."""
    code = """
import math
total = sum(inputs.get('values', [10, 20, 30]))
result = {'total': total, 'sqrt': math.sqrt(total)}
"""
    res = await python_sandbox.execute_script(code, context={"inputs": {"values": [10, 20, 30]}})
    assert res["success"] is True
    res_val = res["result"]
    if isinstance(res_val, str):
        import json
        res_val = json.loads(res_val)
    assert res_val["total"] == 60
    assert round(res_val["sqrt"], 2) == 7.75


@pytest.mark.asyncio
async def test_ssrf_protection_blocklist():
    """Verifies that loopback, private subnets, and cloud metadata IPs are blocked by SSRF defense."""
    # Loopback
    res_loopback = await http_executor.execute_request("http://127.0.0.1:8000/api/v1/health")
    assert res_loopback["status_code"] == 400
    assert "SSRF" in res_loopback["error"] or "prohibited" in res_loopback["error"]

    # AWS/GCP Cloud Metadata
    res_meta = await http_executor.execute_request("http://169.254.169.254/latest/meta-data/")
    assert res_meta["status_code"] == 400
    assert "SSRF" in res_meta["error"] or "prohibited" in res_meta["error"]

    # Private Subnet 192.168.1.1
    res_priv = await http_executor.execute_request("http://192.168.1.1/admin")
    assert res_priv["status_code"] == 400
    assert "SSRF" in res_priv["error"] or "prohibited" in res_priv["error"]


@pytest.mark.asyncio
async def test_data_transform_evaluator():
    """Verifies rule-based extraction, filtering, aggregation, and regex without eval()."""
    # Extract
    data = {"user": {"profile": {"name": "Alice", "age": 30}}}
    assert data_transform_evaluator.transform("extract", data, {"path": "user.profile.name"}) == "Alice"

    # Filter
    items = [{"val": 10}, {"val": 25}, {"val": 5}]
    filtered = data_transform_evaluator.transform("filter", items, {"field": "val", "operator": "greater_than", "value": 15})
    assert len(filtered) == 1
    assert filtered[0]["val"] == 25

    # Aggregate
    assert data_transform_evaluator.transform("aggregate", [10, 20, 30], {"aggregation_type": "average"}) == 20.0


@pytest.mark.asyncio
async def test_workflow_api_full_crud_and_execution(async_client: AsyncClient, auth_headers: dict):
    """End-to-end API test for creating, executing, exporting, importing, multi-tenant isolation, and deleting workflows."""
    headers = auth_headers

    # 1. Create Workflow DAG
    create_res = await async_client.post(
        "/api/v1/workflows",
        headers=headers,
        json={
            "name": "E2E Test DAG",
            "description": "Integration testing workflow studio",
            "nodes": [
                {"id": "start_1", "type": "start", "label": "Start Node"},
                {
                    "id": "py_1",
                    "type": "python_script",
                    "label": "Python Calculator",
                    "data": {"code": "result = inputs.get('x', 5) * 2"},
                },
                {"id": "end_1", "type": "end", "label": "End Node"},
            ],
            "edges": [
                {"id": "e1", "source": "start_1", "target": "py_1"},
                {"id": "e2", "source": "py_1", "target": "end_1"},
            ],
        },
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    wf_data = create_res.json()
    wf_id = wf_data["id"]

    # 2. Run Workflow Execution
    run_res = await async_client.post(
        f"/api/v1/workflows/{wf_id}/run",
        headers=headers,
        json={"inputs": {"x": 21}},
    )
    assert run_res.status_code == status.HTTP_200_OK
    exec_data = run_res.json()
    assert exec_data["status"] == "SUCCESS"
    assert len(exec_data["nodes"]) == 3

    # 3. Export Workflow
    exp_res = await async_client.get(f"/api/v1/workflows/{wf_id}/export", headers=headers)
    assert exp_res.status_code == status.HTTP_200_OK
    exp_json = exp_res.json()
    assert exp_json["name"] == "E2E Test DAG"

    # 4. Import Workflow
    imp_res = await async_client.post("/api/v1/workflows/import", headers=headers, json=exp_json)
    assert imp_res.status_code == status.HTTP_201_CREATED
    imp_data = imp_res.json()
    assert "Imported" in imp_data["name"]

    # 5. Register User B & Test Multi-Tenant Authorization Isolation
    reg_b = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "user_b@neurodesk.ai", "full_name": "User B", "password": "UserBPassword2026!"},
    )
    assert reg_b.status_code == status.HTTP_201_CREATED
    login_b = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "user_b@neurodesk.ai", "password": "UserBPassword2026!"},
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    unauth_res = await async_client.get(f"/api/v1/workflows/{wf_id}", headers=headers_b)
    assert unauth_res.status_code == status.HTTP_404_NOT_FOUND

    unauth_del = await async_client.delete(f"/api/v1/workflows/{wf_id}", headers=headers_b)
    assert unauth_del.status_code == status.HTTP_404_NOT_FOUND

    # 6. Delete Workflow as Owner
    del_res = await async_client.delete(f"/api/v1/workflows/{wf_id}", headers=headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    # Confirm 404 on get
    get_deleted = await async_client.get(f"/api/v1/workflows/{wf_id}", headers=headers)
    assert get_deleted.status_code == status.HTTP_404_NOT_FOUND
