from typing import Any, Dict, List, Optional


class TechStackEngine:
    """Recommends technologies for frontend, backend, database, storage, caching, auth, AI framework, deployment, CI/CD, testing, monitoring with selection rationales."""

    def recommend_tech_stack(self, project_type: str, preferred: Optional[List[str]] = None) -> Dict[str, Any]:
        p_type = project_type.lower()

        recommendations = {
            "frontend": {
                "technology": "React 18 + Vite + Tailwind CSS",
                "why": "Offers low bundle size, fast HMR development, component reusability, and modern responsive UI styling.",
            },
            "backend": {
                "technology": "FastAPI (Python 3.12)",
                "why": "Provides high performance async concurrency, automatic OpenAPI documentation, and native Pydantic schema validation.",
            },
            "database": {
                "technology": "PostgreSQL 16",
                "why": "Proven ACID compliance, strong relational integrity, JSONB semi-structured data support, and pgvector extension for AI search.",
            },
            "storage": {
                "technology": "MinIO / Amazon S3",
                "why": "High-throughput S3-compatible object storage for binary files, document assets, and user uploads.",
            },
            "caching": {
                "technology": "Redis 7.2",
                "why": "Sub-millisecond latency memory cache for session states, rate limiting tokens, and query result caching.",
            },
            "authentication": {
                "technology": "OAuth2 + Stateless JWT (RS256)",
                "why": "Secure multi-tenant authentication with short-lived tokens and refresh token rotation.",
            },
            "ai_framework": {
                "technology": "LangChain + PyTorch / HuggingFace",
                "why": "Modular agent orchestration, prompt templates, vector embeddings, and flexible LLM model integration.",
            },
            "deployment": {
                "technology": "Kubernetes + Docker Compose",
                "why": "Containerized multi-cloud deployment supporting zero-downtime rolling updates and auto-scaling.",
            },
            "ci_cd": {
                "technology": "GitHub Actions",
                "why": "Automated workflow pipelines for linting, security scanning, unit testing, and container registry pushing.",
            },
            "testing": {
                "technology": "Pytest + Vitest",
                "why": "Fast parallel test execution, mocking capabilities, and 100% test coverage verification.",
            },
            "monitoring": {
                "technology": "Prometheus + Grafana",
                "why": "Real-time system metric collection, latency tracking, custom alerts, and visualization dashboards.",
            },
        }

        # Handle user overrides from preferred list if provided
        if preferred:
            for p in preferred:
                p_clean = p.strip()
                p_lower = p_clean.lower()
                if any(w in p_lower for w in ["react", "next", "vue", "angular"]):
                    recommendations["frontend"] = {"technology": p_clean, "why": "Selected based on preferred frontend stack specification."}
                elif any(w in p_lower for w in ["fastapi", "node", "express", "spring", "django", "flask"]):
                    recommendations["backend"] = {"technology": p_clean, "why": "Selected based on preferred backend framework requirement."}
                elif any(w in p_lower for w in ["postgres", "mongo", "mysql"]):
                    recommendations["database"] = {"technology": p_clean, "why": "Selected based on preferred database engine selection."}

        return {
            "recommendations": recommendations,
            "frontend_frameworks": [recommendations["frontend"]["technology"]],
            "backend_frameworks": [recommendations["backend"]["technology"]],
            "databases": [recommendations["database"]["technology"]],
            "devops_infrastructure": [recommendations["deployment"]["technology"], recommendations["ci_cd"]["technology"]],
            "recommended_primary": {
                "frontend": recommendations["frontend"]["technology"],
                "backend": recommendations["backend"]["technology"],
                "database": recommendations["database"]["technology"],
                "devops": recommendations["deployment"]["technology"],
            },
        }


tech_stack_engine = TechStackEngine()
