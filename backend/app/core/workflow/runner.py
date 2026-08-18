import asyncio
import re
import time
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.analysis import analysis_engine
from app.core.knowledge import knowledge_engine
from app.core.workflow.data_transform import data_transform_evaluator
from app.core.workflow.http_executor import http_executor
from app.core.workflow.python_sandbox import python_sandbox
from app.schemas.knowledge import KnowledgeQueryRequest
from app.services.llm_service import llm_service


def resolve_template_variables(template_str: str, context: Dict[str, Any]) -> str:
    """Resolves template placeholders like {input}, {variables.key}, and {node_id.output.field}."""
    if not isinstance(template_str, str):
        return str(template_str)

    res = template_str

    # 1. Substitute {input}
    last_out = context.get("last_output")
    input_str = json_or_str(last_out)
    res = res.replace("{input}", input_str)

    # 2. Substitute {variables.key} or {key}
    variables = context.get("variables", {})
    for k, v in variables.items():
        res = res.replace(f"{{variables.{k}}}", str(v))
        res = res.replace(f"{{{k}}}", str(v))

    # 3. Substitute node output paths like {start_1.output.value} or {node_1.output}
    node_outputs = context.get("node_outputs", {})
    matches = re.findall(r"\{([a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+)\}", res)
    for match in matches:
        parts = match.split(".")
        target_node = parts[0]
        if target_node in node_outputs:
            out_val = node_outputs[target_node]
            if len(parts) > 1 and parts[1] == "output":
                sub_path = ".".join(parts[2:])
                if sub_path and isinstance(out_val, dict):
                    from app.core.workflow.data_transform import get_nested_value
                    extracted = get_nested_value(out_val, sub_path)
                    res = res.replace(f"{{{match}}}", str(extracted if extracted is not None else ""))
                else:
                    res = res.replace(f"{{{match}}}", json_or_str(out_val))

    return res


def json_or_str(val: Any) -> str:
    if isinstance(val, (dict, list)):
        import json
        return json.dumps(val)
    return str(val if val is not None else "")


class WorkflowRunner:
    """Executes individual workflow node logic connecting to platform engines and external tools."""

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
            formatted_prompt = resolve_template_variables(prompt_template, context)

            provider = data.get("provider", "mock")
            model = data.get("model", "neurodesk-mock-v1")

            llm_res = await llm_service.generate_non_streaming(
                provider_name=provider,
                model_name=model,
                prompt=formatted_prompt,
                system_instruction=data.get("system_prompt", "You are NeuroDesk AI executing an automated workflow node step."),
            )
            outputs = {
                "text": llm_res.get("text", ""),
                "response": llm_res.get("text", ""),
                "token_usage": llm_res.get("token_usage", {}),
                "model": model,
            }

        elif node_type == "knowledge_query":
            raw_q = data.get("query")
            query = resolve_template_variables(str(raw_q) if raw_q else "general document knowledge", context)
            if db_session and owner_id:
                req = KnowledgeQueryRequest(query=query, limit=data.get("limit", 5))
                kq = await knowledge_engine.query_knowledge(
                    owner_id=owner_id,
                    req=req,
                    db_session=db_session,
                )
                outputs = {
                    "citations": [c.model_dump(mode="json") for c in kq.citations],
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
            outputs = doc_res.model_dump(mode="json")

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
            outputs = ds_res.model_dump(mode="json")

        elif node_type == "conditional":
            expr = data.get("condition", "True")
            val = False

            # Safe conditional evaluation
            expr_str = resolve_template_variables(str(expr), context).strip()
            if expr_str in ["True", "true", "1", "YES", "yes"]:
                val = True
            elif expr_str in ["False", "false", "0", "NO", "no"]:
                val = False
            else:
                # Comparison expressions like "10 > 5" or "'admin' == 'admin'"
                match = re.match(r"^(['\"]?[\w\s.-]+['\"]?)\s*(==|!=|>|<|>=|<=)\s*(['\"]?[\w\s.-]+['\"]?)$", expr_str)
                if match:
                    left, op, right = match.group(1).strip("'\""), match.group(2), match.group(3).strip("'\"")
                    try:
                        f_left = float(left)
                        f_right = float(right)
                        if op == "==": val = f_left == f_right
                        elif op == "!=": val = f_left != f_right
                        elif op == ">": val = f_left > f_right
                        elif op == "<": val = f_left < f_right
                        elif op == ">=": val = f_left >= f_right
                        elif op == "<=": val = f_left <= f_right
                    except ValueError:
                        if op == "==": val = left == right
                        elif op == "!=": val = left != right
                else:
                    val = bool(context.get("last_output"))

            outputs = {"branch": "true" if val else "false", "condition_passed": val}

        elif node_type in ["data_transform", "transform"]:
            operation = data.get("operation", "extract")
            target_data = context.get("last_output")
            transformed = data_transform_evaluator.transform(operation, target_data, data)
            outputs = {"transformed": transformed, "result": transformed, "operation": operation}

        elif node_type == "variable":
            var_name = data.get("var_name", "temp_var")
            var_val = data.get("var_value", context.get("last_output"))
            var_val_resolved = resolve_template_variables(str(var_val), context) if isinstance(var_val, str) else var_val
            context.get("variables", {})[var_name] = var_val_resolved
            outputs = {"variable": var_name, "value": var_val_resolved}

        elif node_type == "delay":
            secs = min(float(data.get("seconds", 1)), 5.0)
            await asyncio.sleep(secs)
            outputs = {"delayed_seconds": secs}

        elif node_type == "http_request":
            url = resolve_template_variables(data.get("url", "https://httpbin.org/get"), context)
            method = data.get("method", "GET").upper()
            headers = data.get("headers", {})
            json_body = data.get("json_body") or data.get("body")

            res = await http_executor.execute_request(
                url=url,
                method=method,
                headers=headers,
                json_body=json_body if isinstance(json_body, dict) else None,
                timeout_seconds=float(data.get("timeout", 10.0)),
            )
            outputs = res

        elif node_type == "python_script":
            script_code = data.get("code", "result = inputs.get('val', 42)")
            res = await python_sandbox.execute_script(
                code=script_code,
                context=context,
                timeout_seconds=float(data.get("timeout", 5.0)),
            )
            outputs = res

        elif node_type == "export":
            fmt = data.get("format", "markdown")
            outputs = {"format": fmt, "content": f"# Workflow Export Report\n\nResult: {json_or_str(context.get('last_output'))}"}

        elif node_type == "notification":
            msg = resolve_template_variables(data.get("message", "Workflow step completed"), context)
            outputs = {"notification_sent": True, "message": msg}

        else:
            outputs = {"result": f"Executed generic node type '{node_type}'"}

        latency = (time.time() - start_time) * 1000.0
        outputs["latency_ms"] = round(latency, 2)
        return outputs


workflow_runner = WorkflowRunner()
