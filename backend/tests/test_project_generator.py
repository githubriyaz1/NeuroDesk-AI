import pytest
from httpx import AsyncClient

from app.core.project_generator import (
    api_contract_engine,
    architecture_engine,
    cost_estimation_engine,
    database_design_engine,
    export_engine,
    folder_structure_engine,
    prompt_engineering_engine,
    requirement_engine,
    risk_assessment_engine,
    tech_stack_engine,
)


@pytest.mark.asyncio
async def test_sub_engines_unit():
    # 1. Requirement Engine
    reqs = requirement_engine.generate_requirements("Smart Logistics", "AI fleet routing", "web_app")
    assert reqs["title"] == "Smart Logistics"
    assert len(reqs["functional_requirements"]) >= 4
    assert len(reqs["user_roles"]) >= 3
    assert len(reqs["user_stories"]) >= 2
    assert len(reqs["use_cases"]) >= 2
    assert len(reqs["business_rules"]) >= 2

    # 2. Tech Stack Engine
    t_stack = tech_stack_engine.recommend_tech_stack("web_app", ["React", "FastAPI", "PostgreSQL"])
    assert any("React" in f for f in t_stack["frontend_frameworks"])
    assert any("FastAPI" in b for b in t_stack["backend_frameworks"])

    # 3. Architecture Engine
    arch = architecture_engine.design_architecture("Smart Logistics", "web_app", t_stack)
    assert len(arch["layers"]) == 4
    assert "component_diagram" in arch
    assert "module_breakdown" in arch
    assert "authentication_flow" in arch

    # 4. Database Design Engine
    db_schema = database_design_engine.design_database("Smart Logistics", "web_app")
    assert len(db_schema["tables"]) >= 3
    assert "CREATE TABLE users" in db_schema["sql_ddl"]

    # 5. API Contract Engine
    api_spec = api_contract_engine.design_api_contracts("Smart Logistics")
    assert len(api_spec["endpoints"]) >= 5

    # 6. Folder Structure Engine
    folder_tree = folder_structure_engine.generate_folder_structure("Smart Logistics", t_stack)
    assert folder_tree["name"] == "root"

    # 7. Risk & Cost Engines
    risks = risk_assessment_engine.assess_risks("Smart Logistics", t_stack)
    assert len(risks["risks"]) >= 4
    costs = cost_estimation_engine.estimate_costs("Smart Logistics", "web_app")
    assert "development_time" in costs
    assert "total_monthly_estimated" in costs

    # 8. Export Engine (Markdown, JSON, YAML, HTML)
    for fmt in ["markdown", "json", "yaml", "html"]:
        exp = export_engine.export_blueprint({"summary": {"title": "Smart Logistics", "description": "Test"}}, fmt)
        assert exp["format"] == fmt
        assert "Smart Logistics" in exp["content"]


@pytest.mark.asyncio
async def test_project_generator_api_endpoints(async_client: AsyncClient, auth_headers: dict):
    # 1. Generate Blueprint
    payload = {
        "title": "Smart Logistics Platform",
        "description": "AI-driven fleet routing and package delivery tracking engine.",
        "project_type": "web_app",
        "preferred_tech_stack": ["React", "FastAPI", "PostgreSQL"],
    }
    response = await async_client.post(
        "/api/v1/ai-studio/generate", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["title"]
    bp_id = data["id"]

    # 2. List Blueprints
    list_resp = await async_client.get("/api/v1/ai-studio/blueprints", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. Get Details
    detail_resp = await async_client.get(f"/api/v1/ai-studio/blueprints/{bp_id}", headers=auth_headers)
    assert detail_resp.status_code == 200

    # 4. Clone Blueprint
    clone_resp = await async_client.post(f"/api/v1/ai-studio/blueprints/{bp_id}/clone", headers=auth_headers)
    assert clone_resp.status_code == 201
    assert "Copy" in clone_resp.json()["name"]

    # 5. Export Blueprint
    export_resp = await async_client.post(
        "/api/v1/ai-studio/export",
        json={"blueprint_id": bp_id, "format": "markdown"},
        headers=auth_headers,
    )
    assert export_resp.status_code == 200
    assert "content" in export_resp.json()

    # 6. Metrics & Templates
    metrics_resp = await async_client.get("/api/v1/ai-studio/blueprints/metrics", headers=auth_headers)
    assert metrics_resp.status_code == 200

    templates_resp = await async_client.get("/api/v1/ai-studio/blueprints/templates/starter", headers=auth_headers)
    assert templates_resp.status_code == 200
    assert len(templates_resp.json()) >= 1
