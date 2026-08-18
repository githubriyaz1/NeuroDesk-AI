from typing import Any, Dict, List


class ArchitectureEngine:
    """Designs 4-tier enterprise system architecture, component diagrams (JSON), security, scalability, module breakdown, auth flow, and deployment topology."""

    def design_architecture(self, title: str, project_type: str, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        primary_fe = tech_stack.get("recommended_primary", {}).get("frontend", "React 18 + Vite")
        primary_be = tech_stack.get("recommended_primary", {}).get("backend", "FastAPI (Python 3.12)")
        primary_db = tech_stack.get("recommended_primary", {}).get("database", "PostgreSQL 16")

        layers = [
            {"name": "Client Presentation Layer", "component": primary_fe, "description": "Single Page Application (SPA) / UI rendering with responsive design system and state context."},
            {"name": "API Gateway & Ingress Layer", "component": "Reverse Proxy / Nginx", "description": "SSL termination, rate limiting, request validation, CORS, and routing."},
            {"name": "Application Service Layer", "component": primary_be, "description": "Business logic, domain orchestration, authentication verification, and async task handling."},
            {"name": "Persistence & Cache Layer", "component": f"{primary_db} + Redis", "description": "Relational ORM data storage, structured indexing, and memory cache."},
        ]

        component_relationships = [
            {"from": "Client UI", "to": "API Gateway", "protocol": "HTTPS / WSS", "purpose": "User interaction & REST payloads"},
            {"from": "API Gateway", "to": "Backend Service", "protocol": "HTTP / gRPC", "purpose": "Routed backend requests"},
            {"from": "Backend Service", "to": "Database", "protocol": "Async SQL Driver", "purpose": "CRUD transactions & queries"},
            {"from": "Backend Service", "to": "Redis Cache", "protocol": "RESP", "purpose": "Session state & response caching"},
        ]

        component_diagram = {
            "nodes": [
                {"id": "client", "label": "Client UI (SPA)", "type": "frontend", "tech": primary_fe},
                {"id": "gateway", "label": "API Gateway / Nginx", "type": "gateway", "tech": "Reverse Proxy"},
                {"id": "auth_service", "label": "Auth Service", "type": "service", "tech": "OAuth2 / JWT"},
                {"id": "core_service", "label": f"{title} Core Service", "type": "service", "tech": primary_be},
                {"id": "database", "label": "Relational DB", "type": "storage", "tech": primary_db},
                {"id": "redis", "label": "Memory Cache", "type": "cache", "tech": "Redis"},
            ],
            "edges": [
                {"source": "client", "target": "gateway", "label": "HTTPS REST API / WebSocket"},
                {"source": "gateway", "target": "auth_service", "label": "Validate Auth & JWT Tokens"},
                {"source": "gateway", "target": "core_service", "label": "Route Request Payloads"},
                {"source": "core_service", "target": "database", "label": "Async SQLAlchemy CRUD"},
                {"source": "core_service", "target": "redis", "label": "Cache Session State & Keys"},
            ],
        }

        module_breakdown = [
            {"module": "Auth & User Management", "responsibility": "Registration, Login, Password Hashing, JWT issuing, RBAC verification"},
            {"module": "Core Domain Engine", "responsibility": f"Business logic, workflow execution, data processing for {title}"},
            {"module": "Knowledge & RAG Engine", "responsibility": "Document indexing, chunk vector embedding, semantic similarity search"},
            {"module": "Export & Analytics Engine", "responsibility": "Generating JSON/Markdown/PDF exports, usage telemetry, audit reporting"},
        ]

        authentication_flow = [
            "1. User submits login credentials (email & password) to /api/v1/auth/token.",
            "2. Auth Service verifies password hash against bcrypt stored hash in PostgreSQL.",
            "3. Upon successful verification, Auth Service returns RS256-signed JWT Access Token and HTTP-only Refresh Cookie.",
            "4. Client includes Bearer Access Token in Authorization header for subsequent API requests.",
            "5. API Gateway / Middleware decodes JWT, verifies signature & expiry, and injects current user claims into request context.",
        ]

        deployment_architecture = {
            "environment": "Multi-Tenant Containerized Cloud (Kubernetes / Docker Compose)",
            "ingress": "Nginx Ingress Controller with Let's Encrypt TLS certificates",
            "containers": [
                "frontend-ui: nginx Alpine container serving static production bundle",
                "backend-api: uvicorn/gunicorn worker cluster scaling horizontally",
                "database: Managed PostgreSQL instance with automated daily snapshots & read-replicas",
                "cache: Managed Redis Cluster with memory persistence",
            ],
            "ci_cd_pipeline": "Automated GitHub Actions workflow building OCI image tags on push to main branch",
        }

        security_considerations = [
            "OAuth2 / JWT stateless token authentication with short expiry and refresh token rotation.",
            "Role-Based Access Control (RBAC) enforced at service layer boundary.",
            "Input sanitization, parameter binding, and strict Pydantic DTO schema validation to prevent SQLi & XSS.",
            "TLS 1.3 encryption in transit and AES-256 database column encryption at rest.",
        ]

        scalability_recommendations = [
            "Stateless backend design allowing zero-downtime horizontal pod autoscaling (HPA).",
            "Database read replica separation for high-volume query offloading.",
            "Asynchronous message processing for background tasks.",
            "CDN static asset delivery for low-latency global frontend loading.",
        ]

        return {
            "pattern": "4-Tier Microservices / Layered Enterprise Pattern",
            "layers": layers,
            "relationships": component_relationships,
            "component_diagram": component_diagram,
            "module_breakdown": module_breakdown,
            "authentication_flow": authentication_flow,
            "deployment_architecture": deployment_architecture,
            "security": security_considerations,
            "scalability": scalability_recommendations,
        }


architecture_engine = ArchitectureEngine()
