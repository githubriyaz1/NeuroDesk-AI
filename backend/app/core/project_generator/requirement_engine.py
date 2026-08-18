from typing import Any, Dict, List


class RequirementEngine:
    """Generates executive summaries, requirements, user roles, user stories, use cases, and business rules."""

    def generate_requirements(self, title: str, description: str, project_type: str) -> Dict[str, Any]:
        p_type_clean = project_type.replace("_", " ").title()
        
        problem_statement = f"The proposed system addresses operational inefficiencies and manual overhead in managing enterprise workflows and data for {title}."
        objectives = [
            f"Build a scalable {p_type_clean} solution providing real-time data processing.",
            "Ensure enterprise-grade security, role-based access control, and audit compliance.",
            "Deliver an intuitive user interface with low-latency API response times (<200ms).",
            "Provide high availability (99.9% uptime) and automated disaster recovery.",
        ]

        functional_requirements = [
            {"id": "FR-101", "category": "Authentication", "title": "User Authentication & RBAC", "description": "Users must authenticate via JWT tokens or OAuth2 with multi-tenant access control."},
            {"id": "FR-102", "category": "Core Domain", "title": f"Core Management for {title}", "description": f"Core operations to create, edit, view, and process data for {p_type_clean}."},
            {"id": "FR-103", "category": "Analytics", "title": "Real-time Reporting & Metrics", "description": "System must provide metrics, performance analytics, and audit logging."},
            {"id": "FR-104", "category": "Integration", "title": "External Service Integrations", "description": "Support REST API and webhooks for seamless third-party service communication."},
        ]

        non_functional_requirements = [
            {"id": "NFR-201", "category": "Performance", "title": "API Response Latency", "description": "95th percentile API response time must remain under 200ms under 1,000 concurrent requests."},
            {"id": "NFR-202", "category": "Scalability", "title": "Horizontal Scaling", "description": "Stateless service design supporting auto-scaling on Kubernetes/Docker."},
            {"id": "NFR-203", "category": "Security", "title": "Encryption & Compliance", "description": "Data at rest must use AES-256 and transit must enforce TLS 1.3."},
            {"id": "NFR-204", "category": "Accessibility", "title": "WCAG 2.1 AA Compliance", "description": "Frontend UI must adhere to WCAG 2.1 AA standards for full accessibility."},
        ]

        user_roles = [
            {"role": "System Administrator", "permissions": "Full system configuration, user provisioning, audit inspection"},
            {"role": "Project Manager / Lead", "permissions": "Workspace management, blueprint edits, workflow triggers"},
            {"role": "Standard User / Member", "permissions": "View workspace resources, submit queries, export reports"},
            {"role": "Auditor", "permissions": "Read-only access to audit logs and security compliance reports"},
        ]

        user_stories = [
            {"id": "US-01", "as_a": "System Administrator", "i_want_to": "manage user roles and RBAC permissions", "so_that": "I can enforce zero-trust security across organization tenants."},
            {"id": "US-02", "as_a": "Project Lead", "i_want_to": "describe a software idea in plain English", "so_that": "I can automatically generate a 4-tier architectural blueprint and cost estimation."},
            {"id": "US-03", "as_a": "Developer", "i_want_to": "inspect REST API contracts and database DDL schemas", "so_that": "I can rapidly implement compliant backend endpoints and DB migrations."},
        ]

        use_cases = [
            {"id": "UC-101", "name": "Blueprint Generation Flow", "actor": "Project Lead", "precondition": "Authenticated user with active workspace", "postcondition": "Blueprint saved with version snapshot and DDL schema"},
            {"id": "UC-102", "name": "Real-time AI Chat Assistance", "actor": "Standard User", "precondition": "Workspace assets uploaded to KnowledgeEngine", "postcondition": "AI response generated with exact citations"},
        ]

        business_rules = [
            {"id": "BR-01", "rule": "Multi-Tenant Isolation", "description": "All database queries must enforce tenant filter checking owner_id == user_id."},
            {"id": "BR-02", "rule": "Audit Logging", "description": "All administrative changes, role modifications, and asset exports must trigger immutably stored audit events."},
        ]

        return {
            "title": title,
            "problem_statement": problem_statement,
            "objectives": objectives,
            "functional_requirements": functional_requirements,
            "non_functional_requirements": non_functional_requirements,
            "user_roles": user_roles,
            "user_stories": user_stories,
            "use_cases": use_cases,
            "business_rules": business_rules,
        }


requirement_engine = RequirementEngine()
