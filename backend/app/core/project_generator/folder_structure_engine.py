from typing import Any, Dict, List


class FolderStructureEngine:
    """Generates production-grade folder structure trees with boilerplate file paths."""

    def generate_folder_structure(self, title: str, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        primary_fe = tech_stack.get("recommended_primary", {}).get("frontend", "React")
        primary_be = tech_stack.get("recommended_primary", {}).get("backend", "FastAPI")

        tree = {
            "name": "root",
            "type": "directory",
            "children": [
                {
                    "name": "backend",
                    "type": "directory",
                    "children": [
                        {
                            "name": "app",
                            "type": "directory",
                            "children": [
                                {"name": "main.py", "type": "file", "description": "FastAPI application entrypoint and middleware setup"},
                                {"name": "config.py", "type": "file", "description": "Environment variables and Pydantic settings"},
                                {"name": "routers", "type": "directory", "children": [{"name": "auth.py", "type": "file"}, {"name": "projects.py", "type": "file"}]},
                                {"name": "services", "type": "directory", "children": [{"name": "auth_service.py", "type": "file"}, {"name": "project_service.py", "type": "file"}]},
                                {"name": "repositories", "type": "directory", "children": [{"name": "project_repository.py", "type": "file"}]},
                                {"name": "models", "type": "directory", "children": [{"name": "user.py", "type": "file"}, {"name": "project.py", "type": "file"}]},
                                {"name": "schemas", "type": "directory", "children": [{"name": "user.py", "type": "file"}, {"name": "project.py", "type": "file"}]},
                            ],
                        },
                        {"name": "Dockerfile", "type": "file", "description": "Multi-stage production Docker build container"},
                        {"name": "requirements.txt", "type": "file", "description": "Python package dependencies"},
                    ],
                },
                {
                    "name": "frontend",
                    "type": "directory",
                    "children": [
                        {
                            "name": "src",
                            "type": "directory",
                            "children": [
                                {"name": "App.jsx", "type": "file", "description": "Main application component & router setup"},
                                {"name": "main.jsx", "type": "file", "description": "DOM mount entrypoint"},
                                {"name": "components", "type": "directory", "children": [{"name": "Header.jsx", "type": "file"}, {"name": "Sidebar.jsx", "type": "file"}]},
                                {"name": "pages", "type": "directory", "children": [{"name": "DashboardPage.jsx", "type": "file"}, {"name": "LoginPage.jsx", "type": "file"}]},
                                {"name": "services", "type": "directory", "children": [{"name": "api.js", "type": "file"}, {"name": "projectService.js", "type": "file"}]},
                            ],
                        },
                        {"name": "package.json", "type": "file", "description": "NPM package scripts and dependencies"},
                        {"name": "vite.config.js", "type": "file", "description": "Vite bundler configuration"},
                    ],
                },
                {"name": "docker-compose.yml", "type": "file", "description": "Orchestrates PostgreSQL, Redis, Backend, and Frontend containers"},
                {"name": "README.md", "type": "file", "description": "Project documentation and setup instructions"},
            ],
        }

        return tree


folder_structure_engine = FolderStructureEngine()
