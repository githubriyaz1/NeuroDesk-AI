# NeuroDesk AI Enterprise System Architecture

## Architectural Principles

NeuroDesk AI is built adhering to enterprise software engineering standards:

1. **Separation of Concerns**: Clean isolation between UI components, API routes, business logic services, data access layers, and storage providers.
2. **Domain Driven Design (DDD)**: Organization of code around domain models: Auth, Users, Digital Assets (DAMS), Universal Preview Engine (UPE), Workspace, AI Studio, Project Generator, AI Chat, and Workflows.
3. **Pluggable Preview Engine (UPE)**: `PreviewService` manages dynamic provider resolution (`PDFPreviewProvider`, `CSVPreviewProvider`, `ExcelPreviewProvider`, `ImagePreviewProvider`, `UnsupportedPreviewProvider`). New format providers (such as DOCX, PPTX, Audio, or Video) can be added cleanly without modifying `PreviewService`.
4. **Pluggable Storage Layer**: DAMS Core utilizes `StorageService` wrapping abstract `StorageProvider` (defaulting to `LocalStorageProvider` under `storage/uploads/{user_id}/{year}/{month}/`), allowing future cloud providers (AWS S3, Azure Blob, GCS) to plug in with zero changes to business logic.
5. **Stateless API Gateway**: FastAPI backend designed to scale horizontally across multiple container instances with stateless JWT sessions and database-backed refresh token rotation.
6. **Modern Minimalist UI**: Sleek dark-theme design pattern adhering to Vercel/Linear UX guidelines.

## Universal Preview Engine (UPE Subsystem)

### UPE Lifecycle & Provider Resolution
1. **Provider Resolution**:
   - `PreviewService` maintains an ordered list of concrete providers (`PDFPreviewProvider`, `CSVPreviewProvider`, `ExcelPreviewProvider`, `ImagePreviewProvider`).
   - For any target asset, `PreviewService.select_provider(asset)` evaluates `can_handle(asset_type, mime_type, extension)`.
   - If no specialized provider matches, `UnsupportedPreviewProvider` handles the request gracefully.
2. **Preview Payloads**:
   - `PDF`: Extracts page count, document title, author, and page 1 text snippet.
   - `CSV`: Extracts column headers, column count, row count, and first 50 sample data rows.
   - `Excel`: Extracts sheet names, active sheet title, and 50 rows per sheet.
   - `Image`: Extracts width, height, resolution, color mode, format, and aspect ratio.
   - `Unsupported`: Returns `can_preview = False` and explanatory message.

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

## System Component Diagram

```
+-----------------------------------------------------------------------+
|                           CLIENT LAYER                                |
|                                                                       |
|   React 18 + Vite Single Page Application                             |
|   ├── AuthContext (Global Session State & Token Manager)              |
|   ├── AssetContext & useAssets (DAMS State & Upload Queue Manager)    |
|   ├── PreviewDrawer (Universal Preview Engine Modal / Drawer)         |
|   │   └── Renderers: PdfPreview, CsvPreview, ExcelPreview, Image...   |
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
|   ├── UPE Preview Endpoints (/api/v1/assets/{id}/preview, metadata)   |
|   └── Service Layer (AuthService, AssetService, PreviewService)       |
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
