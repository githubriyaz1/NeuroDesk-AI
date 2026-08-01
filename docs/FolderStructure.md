# NeuroDesk AI Comprehensive Folder Structure

```
NeuroDesk-AI/
├── .github/
│   └── workflows/
│       └── ci.yml                     # GitHub Actions CI/CD automation
├── backend/                           # Python FastAPI REST API server
│   ├── app/
│   │   ├── core/                      # System configuration & logging
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Pydantic BaseSettings environment config
│   │   │   └── logging.py             # Custom logging formatters
│   │   ├── database/                  # SQLAlchemy setup
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Declarative base model
│   │   │   └── session.py             # Async engine & sessionmaker generator
│   │   ├── middleware/                # FastAPI custom middleware
│   │   │   ├── __init__.py
│   │   │   ├── cors.py                # CORS headers middleware
│   │   │   ├── exception_handler.py   # Global API exception handlers
│   │   │   └── logging.py             # Request execution timing middleware
│   │   ├── models/                    # DB entity definitions
│   │   │   ├── __init__.py
│   │   │   ├── ai_studio.py           # AI Studio model ORM schema
│   │   │   ├── chat.py                # AI Chat ORM schema
│   │   │   ├── project_generator.py   # AI Blueprint ORM schema
│   │   │   ├── user.py                # User identity ORM schema
│   │   │   ├── workflow.py            # Workflow ORM schema
│   │   │   └── workspace.py           # Workspace ORM schema
│   │   ├── routers/                   # API HTTP route controllers
│   │   │   ├── __init__.py
│   │   │   ├── ai_studio.py           # AI Studio endpoints
│   │   │   ├── api_v1.py              # API v1 Router aggregator
│   │   │   ├── auth.py                # Authentication endpoints
│   │   │   ├── chat.py                # AI Chat endpoints
│   │   │   ├── health.py              # System health check endpoints
│   │   │   ├── project_generator.py   # AI Blueprint Generator endpoints
│   │   │   ├── workflow.py            # Workflow automation endpoints
│   │   │   └── workspace.py           # Workspace dataset endpoints
│   │   ├── schemas/                   # Pydantic validation DTOs
│   │   │   ├── __init__.py
│   │   │   ├── ai_studio.py           # AI Studio DTOs
│   │   │   ├── auth.py                # Auth DTOs
│   │   │   ├── chat.py                # AI Chat DTOs
│   │   │   ├── common.py              # Standard response wrappers
│   │   │   ├── health.py              # Health check DTOs
│   │   │   ├── project_generator.py   # Project Blueprint DTOs
│   │   │   ├── workflow.py            # Workflow DTOs
│   │   │   └── workspace.py           # Workspace DTOs
│   │   ├── services/                  # Encapsulated domain business logic
│   │   │   ├── __init__.py
│   │   │   ├── ai_studio_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── project_generator_service.py
│   │   │   ├── workflow_service.py
│   │   │   └── workspace_service.py
│   │   └── utils/                     # Shared backend utilities
│   │       ├── __init__.py
│   │       ├── response.py            # HTTP response builder
│   │       └── security.py            # Password hashing & JWT helpers
│   ├── tests/                         # Pytest test suite
│   │   ├── __init__.py
│   │   ├── conftest.py                # Test fixtures & HTTP client test setup
│   │   ├── test_generator.py          # AI Project Generator tests
│   │   ├── test_health.py             # Health check tests
│   │   └── test_workspace.py          # Workspace API tests
│   ├── Dockerfile                     # Backend Docker container build
│   ├── pyproject.toml                 # Backend tool configuration
│   └── requirements.txt               # Backend Python package manifest
├── database/                          # PostgreSQL database definitions
│   ├── README.md                      # Database strategy documentation
│   └── schema.sql                     # Reference DDL SQL schema
├── docs/                              # Technical project documentation
│   ├── Architecture.md
│   ├── DevelopmentGuide.md
│   └── FolderStructure.md
├── frontend/                          # React SPA Client
│   ├── src/
│   │   ├── __tests__/                 # Vitest frontend unit tests
│   │   ├── assets/                    # Styling, icons, and theme configuration
│   │   ├── components/                # Modular UI component library
│   │   │   ├── common/                # Buttons, Cards, Modals, Badges, Loaders
│   │   │   └── navigation/            # Sidebar navigation & Top Header bar
│   │   ├── contexts/                  # React Contexts (Auth, Theme)
│   │   ├── hooks/                     # Custom React Hooks
│   │   ├── layouts/                   # Responsive Dashboard Layout
│   │   ├── pages/                     # Full Page Component Views
│   │   ├── services/                  # Axios HTTP Service instances
│   │   └── utils/                     # Constants, formatters, utilities
│   ├── Dockerfile                     # Frontend multi-stage Nginx container
│   ├── nginx.conf                     # Nginx server configuration
│   ├── package.json                   # Dependencies & scripts
│   └── vite.config.js                 # Vite & Vitest configuration
├── scripts/                           # Developer utility scripts
│   ├── setup-env.bat
│   ├── start-dev.bat
│   └── start-dev.ps1
├── .gitignore                         # Version control ignore list
├── docker-compose.yml                 # Local & production Docker stack setup
└── README.md                          # Repository overview & onboarding
```
