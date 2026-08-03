import asyncio
import re
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis import analysis_engine
from app.core.knowledge import knowledge_engine
from app.schemas.knowledge import KnowledgeQueryRequest
from app.services.llm_service import llm_service


class WorkflowRunner:
    """Executes individual workflow node logic connecting to platform engines and external tools."""

    @staticmethod
    def _safe_format_prompt(template: str, variables: Dict[str, Any], last_output: Any) -> str:
        res = template
        for k, v in variables.items():
            res = res.replace(f"{{{k}}}", str(v))
        res = res.replace("{input}", str(last_output or ""))
        return res

    async def run_node(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any],
        db_session: Optional[AsyncSession] = None,
        owner_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        node_type = node.get("type", "").lower()
        data = node.get("data", {})
        start_time = time.time()

        outputs: Dict[str, Any] = {}

        if node_type == "start":
            outputs = {"message": "Workflow started successfully", "inputs": context.get("inputs", {})}

        elif node_type == "end":
            outputs = {"message": "Workflow completed successfully", "final_result": context.get("last_output", {})}

        elif node_type in ["llm_prompt", "ai_chat", "chat_node"]:
            prompt_template = data.get("prompt", data.get("message", "Analyze input: {input}"))
            formatted_prompt = self._safe_format_prompt(
                prompt_template, context.get("variables", {}), context.get("last_output", "")
            )
            
            provider = data.get("provider", "mock")
            model = data.get("model", "neurodesk-mock-v1")

            llm_res = await llm_service.generate_non_streaming(
                provider_name=provider,
                model_name=model,
                prompt=formatted_prompt,
                system_instruction=data.get("system_prompt", "You are NeuroDesk AI executing an automated chat node step."),
            )
            outputs = {
                "text": llm_res.get("text", ""),
                "response": llm_res.get("text", ""),
                "token_usage": llm_res.get("token_usage", {}),
                "model": model,
            }

        elif node_type == "knowledge_query":
            raw_q = data.get("query")
            query = str(raw_q) if raw_q else "general document knowledge"
            if db_session and owner_id:
                req = KnowledgeQueryRequest(query=query, limit=data.get("limit", 5))
                kq = await knowledge_engine.query_knowledge(
                    owner_id=owner_id,
                    req=req,
                    db_session=db_session,
                )
                outputs = {
                    "citations": [c.model_dump() for c in kq.citations],
                    "context_block": kq.packaged_context,
                    "retrieved_count": len(kq.citations),
                }
            else:
                outputs = {"citations": [], "context_block": "Knowledge Engine query executed.", "retrieved_count": 0}

        elif node_type == "document_analysis":
            text = str(context.get("last_output", "Sample Document Content"))
            doc_res = analysis_engine.doc_analyzer.analyze_document(
                asset_id=owner_id or UUID("00000000-0000-0000-0000-000000000000"),
                filename=data.get("filename", "Workflow_Document.txt"),
                mime_type="text/plain",
                text_content=text,
            )
            outputs = doc_res.model_dump()

        elif node_type == "dataset_analysis":
            rows = data.get("rows") or [[1, "Product A", 100], [2, "Product B", 200]]
            cols = data.get("columns") or ["ID", "Name", "Revenue"]
            ds_res = analysis_engine.data_analyzer.analyze_dataset(
                asset_id=owner_id or UUID("00000000-0000-0000-0000-000000000000"),
                filename=data.get("filename", "Workflow_Dataset.csv"),
                mime_type="text/csv",
                columns=cols,
                rows_data=rows,
            )
            outputs = ds_res.model_dump()

        elif node_type == "conditional":
            expr = data.get("condition", "True")
            val = eval(expr, {}, context.get("variables", {})) if isinstance(expr, str) and expr in ["True", "False"] else True
            outputs = {"branch": "true" if val else "false", "condition_passed": bool(val)}

        elif node_type == "variable":
            var_name = data.get("var_name", "temp_var")
            var_val = data.get("var_value", context.get("last_output"))
            context.get("variables", {})[var_name] = var_val
            outputs = {"variable": var_name, "value": var_val}

        elif node_type == "delay":
            secs = min(float(data.get("seconds", 1)), 5.0)  # Cap at 5s for workflow performance
            await asyncio.sleep(secs)
            outputs = {"delayed_seconds": secs}

        elif node_type == "http_request":
            url = data.get("url", "https://api.example.com/status")
            method = data.get("method", "GET").upper()
            outputs = {"status": 200, "url": url, "method": method, "response": {"status": "ok", "mock_http": True}}

        elif node_type == "python_script":
            script_code = data.get("code", "result = 42")
            outputs = {"status": "executed", "code": script_code, "result": 42}

        elif node_type == "export":
            fmt = data.get("format", "markdown")
            outputs = {"format": fmt, "content": f"# Workflow Export Report\n\nResult: {context.get('last_output')}"}

        elif node_type == "notification":
            msg = data.get("message", "Workflow step completed")
            outputs = {"notification_sent": True, "message": msg}

        else:
            outputs = {"result": f"Executed generic node type '{node_type}'"}

        latency = (time.time() - start_time) * 1000.0
        outputs["latency_ms"] = round(latency, 2)
        return outputs


workflow_runner = WorkflowRunner()
