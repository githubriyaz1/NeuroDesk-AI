from typing import Any, Dict, List
from app.core.workflow.validator import workflow_validator


class WorkflowCompiler:
    """Compiles workflow nodes and edges into a topologically sorted DAG execution plan."""

    @staticmethod
    def compile_plan(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        is_valid, errors = workflow_validator.validate_graph(nodes, edges)
        if not is_valid:
            raise ValueError(f"Workflow compilation failed: {'; '.join(errors)}")

        node_map = {n["id"]: n for n in nodes}
        in_degree = {n["id"]: 0 for n in nodes}
        adj: Dict[str, List[str]] = {n["id"]: [] for n in nodes}

        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            adj[src].append(tgt)
            in_degree[tgt] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        execution_order = []

        while queue:
            curr_id = queue.pop(0)
            execution_order.append(node_map[curr_id])
            for neighbor in adj[curr_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return execution_order


workflow_compiler = WorkflowCompiler()
