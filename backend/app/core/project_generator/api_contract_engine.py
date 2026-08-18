from typing import Any, Dict, List


class APIContractEngine:
    """Designs REST API endpoints, DTO models, HTTP methods, status codes, and authentication strategy."""

    def design_api_contracts(self, title: str) -> Dict[str, Any]:
        endpoints = [
            {
                "path": "/api/v1/auth/register",
                "method": "POST",
                "summary": "Register a new user account",
                "request_body": {"email": "string", "password": "string"},
                "response_body": {"id": "uuid", "email": "string", "role": "string"},
                "status_code": 201,
                "auth_required": False,
            },
            {
                "path": "/api/v1/auth/login",
                "method": "POST",
                "summary": "Authenticate user and issue JWT tokens",
                "request_body": {"email": "string", "password": "string"},
                "response_body": {"access_token": "string", "token_type": "bearer", "expires_in": 1800},
                "status_code": 200,
                "auth_required": False,
            },
            {
                "path": "/api/v1/projects",
                "method": "GET",
                "summary": "List all tenant projects with pagination",
                "request_body": None,
                "response_body": [{"id": "uuid", "title": "string", "status": "string", "created_at": "datetime"}],
                "status_code": 200,
                "auth_required": True,
            },
            {
                "path": "/api/v1/projects",
                "method": "POST",
                "summary": "Create a new project entry",
                "request_body": {"title": "string", "description": "string"},
                "response_body": {"id": "uuid", "title": "string", "status": "string"},
                "status_code": 201,
                "auth_required": True,
            },
            {
                "path": "/api/v1/projects/{id}",
                "method": "GET",
                "summary": "Get full details of a specific project",
                "request_body": None,
                "response_body": {"id": "uuid", "title": "string", "status": "string", "metadata": "object"},
                "status_code": 200,
                "auth_required": True,
            },
            {
                "path": "/api/v1/projects/{id}",
                "method": "PUT",
                "summary": "Update an existing project entry",
                "request_body": {"title": "string", "status": "string"},
                "response_body": {"id": "uuid", "title": "string", "status": "string"},
                "status_code": 200,
                "auth_required": True,
            },
            {
                "path": "/api/v1/projects/{id}",
                "method": "DELETE",
                "summary": "Delete a project entry",
                "request_body": None,
                "response_body": {"message": "Project deleted successfully"},
                "status_code": 200,
                "auth_required": True,
            },
        ]

        auth_strategy = {
            "type": "Bearer JWT (JSON Web Token)",
            "header": "Authorization: Bearer <JWT_TOKEN>",
            "algorithm": "HS256",
            "expiration_minutes": 30,
            "refresh_token_strategy": "HttpOnly Secure Cookie with 7-day expiry",
        }

        return {
            "version": "v1",
            "base_url": "/api/v1",
            "endpoints": endpoints,
            "authentication_strategy": auth_strategy,
        }


api_contract_engine = APIContractEngine()
