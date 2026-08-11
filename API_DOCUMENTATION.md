# NeuroDesk AI — Complete REST API Documentation

## Overview

The NeuroDesk AI REST API operates under base path `/api/v1`. Authentication uses standard JWT Bearer tokens passed via `Authorization: Bearer <TOKEN>` HTTP headers.

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### `POST /api/v1/auth/register`
- **Auth**: None
- **Request Body**:
  ```json
  {
    "email": "user@neurodesk.ai",
    "password": "SecurePassword2026!",
    "full_name": "Developer User"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "uuid",
    "email": "user@neurodesk.ai",
    "full_name": "Developer User",
    "role": "user",
    "created_at": "2026-08-11T15:00:00Z"
  }
  ```

### `POST /api/v1/auth/login`
- **Auth**: None
- **Request Body**:
  ```json
  {
    "email": "user@neurodesk.ai",
    "password": "SecurePassword2026!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { "id": "uuid", "email": "user@neurodesk.ai", "full_name": "Developer User" }
  }
  ```

---

## 2. Asset & Workspace Management Endpoints (`/api/v1/assets`, `/api/v1/workspace`)

### `POST /api/v1/assets/upload`
- **Auth**: Required (Bearer)
- **Request**: `multipart/form-data` with `file` attachment.
- **Response (201 Created)**:
  ```json
  {
    "id": "asset-uuid",
    "name": "Architecture_Spec.pdf",
    "asset_type": "document",
    "file_size": 1048576,
    "mime_type": "application/pdf"
  }
  ```

### `GET /api/v1/assets`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: Array of asset objects owned by the authenticated user.

### `DELETE /api/v1/assets/{id}`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: `{"message": "Asset deleted successfully"}`.

### `GET /api/v1/workspace/metrics`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: Workspace statistics (`total_assets`, `documents_count`, `datasets_count`, `total_storage_bytes`).

---

## 3. AI Chat & SSE Streaming Endpoints (`/api/v1/chat`)

### `POST /api/v1/chat/stream`
- **Auth**: Required (Bearer)
- **Request Body**:
  ```json
  {
    "conversation_id": "optional-conv-uuid",
    "prompt": "Explain page 1",
    "attached_asset_ids": ["asset-uuid"]
  }
  ```
- **Response (200 OK - `text/event-stream`)**: SSE Event Stream yielding response tokens, grounded citations, and final metadata.

### `GET /api/v1/chat/conversations`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: User's chat conversation history list.

---

## 4. Workflow Studio Endpoints (`/api/v1/workflows`)

### `POST /api/v1/workflows`
- **Auth**: Required (Bearer)
- **Request Body**:
  ```json
  {
    "name": "Data Ingestion Pipeline",
    "nodes": [
      { "id": "s1", "type": "start", "label": "Start" },
      { "id": "e1", "type": "end", "label": "End" }
    ],
    "edges": [
      { "id": "edge1", "source": "s1", "target": "e1" }
    ]
  }
  ```
- **Response (201 Created)**: Workflow object with assigned `id`.

### `POST /api/v1/workflows/{id}/run`
- **Auth**: Required (Bearer)
- **Request Body**: `{"inputs": {}}`
- **Response (200 OK)**: Execution output payload including final result, node statuses, and execution latency.

### `DELETE /api/v1/workflows/{id}`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: `{"message": "Workflow deleted successfully"}`.

### `GET /api/v1/workflows/{id}/export`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: Downloadable JSON export structure.

### `POST /api/v1/workflows/import`
- **Auth**: Required (Bearer)
- **Request Body**: Workflow JSON payload.
- **Response (201 Created)**: Imported workflow object.

---

## 5. Project Generator & AI Studio (`/api/v1/generator`, `/api/v1/ai-studio`)

### `POST /api/v1/generator/generate`
- **Auth**: Required (Bearer)
- **Request Body**: `{"requirements": "Build a real-time analytics web app"}`
- **Response (200 OK)**: Comprehensive system architecture blueprint, tech stack, and risk matrix.

### `GET /api/v1/ai-studio/models`
- **Auth**: Required (Bearer)
- **Response (200 OK)**: List of supported LLM models (`gemini-2.5-flash`, `neurodesk-mock-v1`).
