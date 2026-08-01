# NeuroDesk AI Enterprise System Architecture

## Architectural Principles

NeuroDesk AI is built adhering to enterprise software engineering standards:

1. **Separation of Concerns**: Clean isolation between UI components, API routes, business logic services, data access layers, and infrastructure settings.
2. **Domain Driven Design (DDD)**: Organization of code around domain models: Auth, Users, Workspace, AI Studio, Project Generator, AI Chat, and Workflows.
3. **Pluggable & Extensible**: Modular design allowing effortless replacement of authentication providers, database drivers, or LLM providers.
4. **Stateless API Gateway**: FastAPI backend designed to scale horizontally across multiple container instances with stateless JWT sessions and database-backed refresh token rotation.
5. **Modern Minimalist UI**: Sleek dark-theme design pattern adhering to Vercel/Linear UX guidelines.

## Authentication & Security Subsystem

### Dual Token Lifecycle & Token Rotation
1. **Access Token**:
   - Format: Signed JWT (HS256) containing `sub` (User UUID), `exp` (30 minutes), and `type: "access"`.
   - Transport: Transmitted via HTTP Header (`Authorization: Bearer <access_token>`).
   - Validation: Stateless verification via FastAPI dependency `get_current_user`.
2. **Refresh Token**:
   - Format: Cryptographic 64-character URL-safe string.
   - Storage: SHA-256 hash stored in PostgreSQL `refresh_tokens` table.
   - Lifetime: 7 days.
   - Rotation Policy: Upon calling `/auth/refresh`, the old refresh token is marked `revoked = True` and a brand new refresh token is issued alongside a new access token.
3. **Password Security**:
   - Hashed using `bcrypt` (Passlib). No plaintext passwords stored.

## System Component Diagram

```
+-----------------------------------------------------------------------+
|                           CLIENT LAYER                                |
|                                                                       |
|   React 18 + Vite Single Page Application                             |
|   ├── AuthContext (Global Session State & Token Manager)              |
|   ├── ProtectedRoute Guard (Redirects unauthenticated to /login)      |
|   ├── Pages: Login, Register, Profile, Workspace, AI Studio...        |
|   └── Axios Interceptors (Auto Token Refresh on HTTP 401)             |
+-----------------------------------┬-----------------------------------+
                                    | REST API Calls (JSON)
                                    v
+-----------------------------------------------------------------------+
|                           BACKEND LAYER                               |
|                                                                       |
|   FastAPI Application Gateway                                         |
|   ├── CORS & Security Middleware                                      |
|   ├── Request Timing & Logging Middleware                             |
|   ├── Centralized Exception Handlers                                  |
|   ├── Auth Router (/api/v1/auth/register, login, refresh, logout)     |
|   └── Users Router (/api/v1/users/me, profile, change-password)       |
|                                                                       |
|   Business Logic Services                                             |
|   ├── AuthService             - Registration, bcrypt, JWT rotation    |
|   ├── WorkspaceService        - Dataset & Doc ingestion logic         |
|   ├── AIStudioService         - Model lifecycle & metrics             |
|   ├── ProjectGeneratorService - AI Blueprint planning generator       |
|   ├── AIChatService           - Contextual LLM conversation           |
|   └── WorkflowService         - Pipeline automation logic             |
+-----------------------------------┬-----------------------------------+
                                    | SQLAlchemy 2.0 Async ORM
                                    v
+-----------------------------------------------------------------------+
|                          DATABASE LAYER                               |
|                                                                       |
|   PostgreSQL 16 Relational Engine                                     |
|   ├── Connection Pool via asyncpg                                     |
|   └── Tables: users, refresh_tokens, workspaces, ai_models, workflows |
+-----------------------------------------------------------------------+
```
