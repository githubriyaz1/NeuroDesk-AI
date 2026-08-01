# NeuroDesk AI Enterprise System Architecture

## Architectural Principles

NeuroDesk AI is built adhering to enterprise software engineering standards:

1. **Separation of Concerns**: Clean isolation between UI components, API routes, business logic services, data access layers, and storage providers.
2. **Domain Driven Design (DDD)**: Organization of code around domain models: Auth, Users, Digital Assets (DAMS), Workspace, AI Studio, Project Generator, AI Chat, and Workflows.
3. **Pluggable Storage Layer**: DAMS Core utilizes `StorageService` wrapping abstract `StorageProvider` (defaulting to `LocalStorageProvider` under `storage/uploads/{user_id}/{year}/{month}/`), allowing future cloud providers (AWS S3, Azure Blob, GCS) to plug in with zero changes to business logic.
4. **Stateless API Gateway**: FastAPI backend designed to scale horizontally across multiple container instances with stateless JWT sessions and database-backed refresh token rotation.
5. **Modern Minimalist UI**: Sleek dark-theme design pattern adhering to Vercel/Linear UX guidelines.

## Digital Asset Management System (DAMS Core)

### DAMS Lifecycle & Storage Architecture
1. **Asset Model**:
   - `UUID` primary public key (`id`).
   - Ownership bound to `owner_id` (User UUID).
   - Categorized into 9 strict Asset Types: `DOCUMENT`, `SPREADSHEET`, `DATASET`, `IMAGE`, `AUDIO`, `REPORT`, `PROMPT`, `MODEL`, `VIDEO`.
   - Tracked across 7 Asset Statuses: `CREATED`, `UPLOADING`, `PROCESSING`, `READY`, `FAILED`, `ARCHIVED`, `DELETED`.
2. **Storage Isolation**:
   - Internal physical storage path (`storage_path`) is **never** exposed to the frontend API client.
   - File downloads are served via authorized, streaming API endpoints (`GET /api/v1/assets/{id}/download`).
   - Files stored on disk under `storage/uploads/{user_id}/{year}/{month}/{unique_filename}` to avoid directory bloat and filename collisions.
   - SHA-256 checksums computed during upload stream for integrity verification.
3. **Soft Deletion & Recovery**:
   - Deleting an asset sets `is_deleted = True` and `status = DELETED` with `deleted_at` timestamp.
   - Soft-deleted assets can be restored via `POST /api/v1/assets/{id}/restore`.

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
   - Hashed using native `bcrypt`. No plaintext passwords stored.

## System Component Diagram

```
+-----------------------------------------------------------------------+
|                           CLIENT LAYER                                |
|                                                                       |
|   React 18 + Vite Single Page Application                             |
|   ├── AuthContext (Global Session State & Token Manager)              |
|   ├── AssetContext & useAssets (DAMS State & Upload Queue Manager)    |
|   ├── ProtectedRoute Guard (Redirects unauthenticated to /login)      |
|   ├── Pages: Login, Register, Profile, Workspace DAMS, AI Studio...   |
|   └── Axios Interceptors (Auto Token Refresh on HTTP 401)             |
+-----------------------------------┬-----------------------------------+
                                    | REST API Calls (JSON & Multipart)
                                    v
+-----------------------------------------------------------------------+
|                           BACKEND LAYER                               |
|                                                                       |
|   FastAPI Application Gateway                                         |
|   ├── CORS & Security Middleware                                      |
|   ├── Request Timing & Logging Middleware                             |
|   ├── Centralized Exception Handlers                                  |
|   ├── Auth Router (/api/v1/auth/register, login, refresh, logout)     |
|   ├── Users Router (/api/v1/users/me, profile, change-password)       |
|   ├── Assets Router (/api/v1/assets/upload, download, list, stats...) |
|   └── Service Layer (AuthService, AssetService, StorageService)       |
+-----------------------------------┬-----------------------------------+
                                    | Async DB & Storage Operations
                                    v
+-----------------------------------┴-----------------------------------+
|                        DATA & STORAGE LAYER                           |
|                                                                       |
|   ├── PostgreSQL 16 DB (users, refresh_tokens, assets, workspaces)    |
|   └── Pluggable Storage (LocalStorageProvider -> storage/uploads/...) |
+-----------------------------------------------------------------------+
```
