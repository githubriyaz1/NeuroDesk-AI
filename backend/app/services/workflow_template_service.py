from typing import Any, Dict, List
from app.schemas.workflow import WorkflowNodeSchema, WorkflowEdgeSchema, WorkflowTemplateResponse


class WorkflowTemplateService:
    """Provides starter enterprise workflow templates for instant orchestration."""

    @staticmethod
    def get_starter_templates() -> List[WorkflowTemplateResponse]:
        return [
            WorkflowTemplateResponse(
                id="template-rag-audit",
                name="RAG Knowledge Audit Pipeline",
                description="Queries Knowledge Engine, summarizes retrieved documents with LLM, and exports report.",
                category="RAG & Knowledge",
                nodes=[
                    WorkflowNodeSchema(id="n1", type="start", label="Start", position={"x": 50, "y": 150}),
                    WorkflowNodeSchema(id="n2", type="knowledge_query", label="Knowledge Query", position={"x": 250, "y": 150}, data={"query": "financial Q3 growth"}),
                    WorkflowNodeSchema(id="n3", type="llm_prompt", label="LLM Summarizer", position={"x": 480, "y": 150}, data={"prompt": "Summarize citations: {input}"}),
                    WorkflowNodeSchema(id="n4", type="export", label="Export Report", position={"x": 700, "y": 150}, data={"format": "markdown"}),
                    WorkflowNodeSchema(id="n5", type="end", label="End", position={"x": 900, "y": 150}),
                ],
                edges=[
                    WorkflowEdgeSchema(id="e1-2", source="n1", target="n2"),
                    WorkflowEdgeSchema(id="e2-3", source="n2", target="n3"),
                    WorkflowEdgeSchema(id="e3-4", source="n3", target="n4"),
                    WorkflowEdgeSchema(id="e4-5", source="n4", target="n5"),
                ],
            ),
            WorkflowTemplateResponse(
                id="template-data-analyst",
                name="Automated Dataset Analysis Pipeline",
                description="Performs tabular dataset profiling, generates AI insights, and sends notification.",
                category="Data Analysis",
                nodes=[
                    WorkflowNodeSchema(id="n1", type="start", label="Start", position={"x": 50, "y": 150}),
                    WorkflowNodeSchema(id="n2", type="dataset_analysis", label="Dataset Profiler", position={"x": 250, "y": 150}),
                    WorkflowNodeSchema(id="n3", type="llm_prompt", label="AI Insights Generator", position={"x": 480, "y": 150}, data={"prompt": "Generate strategic recommendations for dataset: {input}"}),
                    WorkflowNodeSchema(id="n4", type="notification", label="Send Notification", position={"x": 700, "y": 150}),
                    WorkflowNodeSchema(id="n5", type="end", label="End", position={"x": 900, "y": 150}),
                ],
                edges=[
                    WorkflowEdgeSchema(id="e1-2", source="n1", target="n2"),
                    WorkflowEdgeSchema(id="e2-3", source="n2", target="n3"),
                    WorkflowEdgeSchema(id="e3-4", source="n3", target="n4"),
                    WorkflowEdgeSchema(id="e4-5", source="n4", target="n5"),
                ],
            ),
        ]


workflow_template_service = WorkflowTemplateService()
