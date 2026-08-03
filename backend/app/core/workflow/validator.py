from typing import Any, Dict, List, Tuple


class WorkflowValidator:
    """Validates workflow graph connectivity, detects cycles, and ensures required nodes exist."""

    @staticmethod
    def validate_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        errors = []
        if not nodes:
            return False, ["Workflow graph must contain at least one node."]

        node_ids = {n["id"] for n in nodes}
        node_types = {n.get("type", "").lower() for n in nodes}

        if "start" not in node_types:
            errors.append("Workflow must contain a 'Start' node.")

        # Check edge endpoints
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if src not in node_ids:
                errors.append(f"Edge {edge.get('id')} references non-existent source node '{src}'.")
            if tgt not in node_ids:
                errors.append(f"Edge {edge.get('id')} references non-existent target node '{tgt}'.")

        # Cycle detection via Kahn's algorithm
        in_degree = {nid: 0 for nid in node_ids}
        adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if src in adj and tgt in in_degree:
                adj[src].append(tgt)
                in_degree[tgt] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count < len(node_ids):
            errors.append("Workflow graph contains a directed cycle. Only Directed Acyclic Graphs (DAGs) are supported.")

        return len(errors) == 0, errors


workflow_validator = WorkflowValidator()
