from typing import Any, Dict, List


class PromptEngineeringEngine:
    """Generates system prompts, prompt templates, and agent roles for automated code generation."""

    def generate_prompts(self, title: str, project_type: str, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        primary_fe = tech_stack.get("recommended_primary", {}).get("frontend", "React")
        primary_be = tech_stack.get("recommended_primary", {}).get("backend", "FastAPI")

        system_prompt = (
            f"You are an expert Principal AI Software Architect specializing in {project_type.replace('_', ' ')}. "
            f"Your objective is to generate production-grade code for '{title}' using {primary_fe} and {primary_be}. "
            "Enforce strict clean architecture, 100% test coverage, comprehensive error handling, and security best practices."
        )

        agent_roles = [
            {"role": "Lead Architect", "focus": "System architecture, layer isolation, and API contract design"},
            {"role": "Backend Specialist", "focus": f"Production logic in {primary_be}, ORM models, and database migrations"},
            {"role": "Frontend Specialist", "focus": f"Component design in {primary_fe}, state management, and UX responsiveness"},
            {"role": "DevOps & Security Engineer", "focus": "Docker containerization, CI/CD pipelines, and secret management"},
        ]

        code_gen_prompts = {
            "backend_boilerplate": f"Generate {primary_be} entrypoint main file with CORS middleware, health check, and route registration.",
            "frontend_boilerplate": f"Generate {primary_fe} root component with theme provider, router setup, and navigation layout.",
            "database_migration": "Generate database migration scripts and ORM declarative models.",
        }

        return {
            "system_prompt": system_prompt,
            "agent_roles": agent_roles,
            "code_gen_prompts": code_gen_prompts,
        }


prompt_engineering_engine = PromptEngineeringEngine()
