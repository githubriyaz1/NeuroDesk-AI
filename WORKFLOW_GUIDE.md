# NeuroDesk AI — Visual Workflow Studio Developer Guide

## Overview

The **NeuroDesk AI Workflow Studio** is an enterprise DAG (Directed Acyclic Graph) automation canvas allowing users to visually orchestrate data ingestion, automated LLM analysis, Python script execution, HTTP requests, data transformations, and conditional branching.

---

## 1. Supported Workflow Node Catalog

| Node Type | Category | Purpose | Key Inputs / Config | Outputs Payload |
| :--- | :--- | :--- | :--- | :--- |
| `start` | Control | Execution entrypoint | Initial execution `inputs` | `{"message": "Started", "inputs": {...}}` |
| `end` | Control | Execution terminal node | Final node payload | `{"final_result": {...}}` |
| `llm_prompt` | AI | Calls LLM generation | `prompt`, `system_prompt`, `provider`, `model` | `{"text": "...", "token_usage": {...}}` |
| `python_script` | Execution | Runs secure Python code | `code`, `timeout` | `{"success": true, "result": {...}}` |
| `http_request` | Tools | Executes HTTP request | `url`, `method`, `headers`, `json_body` | `{"status_code": 200, "body": {...}}` |
| `data_transform` | Transform | Rule-based data mapping | `operation`, `field`, `operator`, `value` | `{"transformed": [...]}` |
| `conditional` | Logic | Evaluates branch condition | `condition` (`"10 > 5"`, `inputs.role == 'admin'`) | `{"branch": "true"` / `"false"}` |
| `variable` | Data | Sets workflow variable | `var_name`, `var_value` | `{"variable": "key", "value": "val"}` |
| `delay` | Control | Safe pause (max 5.0s) | `seconds` | `{"delayed_seconds": 2.0}` |
| `knowledge_query` | RAG | Queries Knowledge Engine | `query`, `limit` | `{"citations": [...], "context": "..."}` |
| `document_analysis`| Analysis | Document feature analysis | `filename`, `mime_type` | `{"entities": [...], "summary": "..."}` |
| `dataset_analysis` | Analysis | Dataset summary metrics | `rows`, `columns` | `{"row_count": X, "summary": {...}}` |
| `export` | Output | Formats final export | `format` (`markdown`/`json`) | `{"format": "markdown", "content": "..."}` |
| `notification` | Tools | Sends workflow alert | `message` | `{"notification_sent": true}` |

---

## 2. Python Sandbox Security Executor (`python_sandbox.py`)

- **Subprocess Isolation**: Scripts run in an isolated subprocess (`asyncio.create_subprocess_exec`) with environment secrets stripped.
- **AST Security Auditing**: Pre-audits AST before execution. Blocks forbidden imports (`os`, `sys`, `subprocess`, `socket`, `shutil`, `ctypes`, etc.) and calls (`exec`, `eval`, `open`, `__import__`, `__builtins__`, `__subclasses__`).
- **Timeout**: Enforces a strict 5.0-second execution limit.

---

## 3. SSRF-Protected HTTP Request Executor (`http_executor.py`)

- **SSRF Defense Engine**: Validates protocol (`http`/`https`), performs DNS resolution via `socket.getaddrinfo`, and checks IP addresses against blocklists (`127.0.0.1`, `localhost`, `::1`, `169.254.169.254`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- **Limits**: Maximum 2 MB response payload limit and 10.0s request timeout.

---

## 4. Conditional Branch Routing & Status `SKIPPED`

When a `conditional` node evaluates to `"true"` or `"false"`, the DAG executor (`executor.py`):
1. Routes execution along out-edges matching `source_handle` (`"true"` or `"false"`).
2. Deactivates unselected branches.
3. Automatically assigns status `SKIPPED` to downstream nodes on inactive handles.

---

## 5. Variable Interpolation Syntax

Workflow text fields support dynamic variable interpolation:
- `{input}`: Output of the immediately preceding node.
- `{variables.key}`: Named variable stored in `context["variables"]`.
- `{node_id.output.path}`: Nested property from a specific previous node output (e.g. `{start_1.output.inputs.user_id}`).

---

## 6. Import and Export Specification

Workflows can be exported to and imported from standard JSON files containing graph node coordinates, edge handles, and variable definitions:

```json
{
  "name": "E2E Data Sync Workflow",
  "description": "Automated data ingestion DAG",
  "nodes": [
    { "id": "start_1", "type": "start", "label": "Start Node" },
    { "id": "py_1", "type": "python_script", "label": "Calculator", "data": { "code": "result = 42" } },
    { "id": "end_1", "type": "end", "label": "End Node" }
  ],
  "edges": [
    { "id": "e1", "source": "start_1", "target": "py_1" },
    { "id": "e2", "source": "py_1", "target": "end_1" }
  ],
  "variables": {}
}
```
