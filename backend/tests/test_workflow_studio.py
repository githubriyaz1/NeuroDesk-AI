import pytest
from httpx import AsyncClient

from app.core.workflow import workflow_compiler, workflow_engine, workflow_validator
from app.services.workflow_service import workflow_service
from app.services.workflow_template_service import workflow_template_service


@pytest.mark.asyncio
async def test_workflow_validator_and_compiler():
    nodes = [
        {"id": "n1", "type": "start", "label": "Start"},
        {"id": "n2", "type": "llm_prompt", "label": "LLM Step"},
        {"id": "n3", "type": "end", "label": "End"},
    ]
    edges = [
        {"id": "e1", "source": "n1", "target": "n2"},
        {"id": "e2", "source": "n2", "target": "n3"},
    ]

    is_valid, errors = workflow_validator.validate_graph(nodes, edges)
    assert is_valid is True
    assert len(errors) == 0

    plan = workflow_compiler.compile_plan(nodes, edges)
    assert len(plan) == 3
    assert plan[0]["id"] == "n1"
    assert plan[2]["id"] == "n3"


@pytest.mark.asyncio
async def test_workflow_cycle_detection():
    nodes = [
        {"id": "n1", "type": "start", "label": "Start"},
        {"id": "n2", "type": "llm_prompt", "label": "LLM Step"},
    ]
    edges = [
        {"id": "e1", "source": "n1", "target": "n2"},
        {"id": "e2", "source": "n2", "target": "n1"},  # Cycle!
    ]

    is_valid, errors = workflow_validator.validate_graph(nodes, edges)
    assert is_valid is False
    assert any("cycle" in err.lower() for err in errors)


@pytest.mark.asyncio
async def test_workflow_starter_templates():
    templates = workflow_template_service.get_starter_templates()
    assert len(templates) >= 2
    assert templates[0].id == "template-rag-audit"


@pytest.mark.asyncio
async def test_workflow_api_endpoints(async_client: AsyncClient, auth_headers: dict):
    # 1. Create Workflow
    payload = {
        "name": "RAG Audit Workflow",
        "description": "Automated RAG knowledge audit graph",
        "nodes": [
            {"id": "n1", "type": "start", "label": "Start", "position": {"x": 0, "y": 0}},
            {"id": "n2", "type": "knowledge_query", "label": "Knowledge Query", "position": {"x": 100, "y": 0}},
            {"id": "n3", "type": "end", "label": "End", "position": {"x": 200, "y": 0}},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n3"},
        ],
        "variables": {"test_var": "hello"},
    }

    create_resp = await async_client.post("/api/v1/workflows", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    wf_data = create_resp.json()
    wf_id = wf_data["id"]
    assert wf_data["name"] == "RAG Audit Workflow"

    # 2. List Workflows
    list_resp = await async_client.get("/api/v1/workflows", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. Get Workflow Details
    detail_resp = await async_client.get(f"/api/v1/workflows/{wf_id}", headers=auth_headers)
    assert detail_resp.status_code == 200

    # 4. Run Workflow Execution
    run_resp = await async_client.post(f"/api/v1/workflows/{wf_id}/run", json={"inputs": {}}, headers=auth_headers)
    assert run_resp.status_code == 200
    exec_data = run_resp.json()
    assert exec_data["status"] == "SUCCESS", f"Error msg: {exec_data.get('error_message')}"
    assert len(exec_data["nodes"]) == 3

    # 5. Get Workflow Metrics
    metrics_resp = await async_client.get("/api/v1/workflows/metrics", headers=auth_headers)
    assert metrics_resp.status_code == 200
    assert metrics_resp.json()["total_executions"] >= 1
