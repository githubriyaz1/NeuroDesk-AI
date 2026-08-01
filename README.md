# NeuroDesk AI 🧠⚡

> Enterprise AI-Powered Intelligent Workspace for Data Analysis, AI Studio Modeling, Automated Workflows, Digital Asset Management (DAMS), and AI-Assisted Project Architecture.

[![CI/CD Pipeline](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?style=flat&logo=react)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![JWT Auth](https://img.shields.io/badge/Auth-JWT%20%2B%20Rotation-indigo.svg?style=flat&logo=json-web-tokens)](https://jwt.io)
[![DAMS Core](https://img.shields.io/badge/Storage-DAMS%20Core-emerald.svg?style=flat&logo=files)](https://jwt.io)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg?style=flat&logo=docker)](https://www.docker.com)

---

## 📌 Executive Overview

**NeuroDesk AI** is an enterprise-grade intelligent workspace designed to unify digital asset management, machine learning lifecycle management, conversational AI analytics, automated pipeline orchestration, and AI-driven software project blueprinting into a single sleek interface.

NeuroDesk AI incorporates a production-ready **Digital Asset Management System (DAMS Core)** serving as the centralized repository for all datasets, model weights, prompts, documents, images, and reports across the ecosystem.

---

## 📁 Digital Asset Management System (DAMS Core Architecture)

The DAMS Core provides a pluggable storage provider abstraction (`StorageService` $\rightarrow$ `LocalStorageProvider` / S3 / GCS) ensuring business logic remains independent of physical storage mechanics.

```
+------------------+                    +------------------+                    +---------------------+
|   React Client   |                    | FastAPI DAMS API |                    | Pluggable Storage   |
+--------+---------+                    +--------+---------+                    +----------+----------+
         |                                       |                                         |
         | --- POST /api/v1/assets/upload ------>| -- Stream & Compute SHA256 ------------>|
         |                                       | -- Write to storage/uploads/{u}/{y}/{m}/->|
         |                                       | -- Save metadata to PostgreSQL -------->|
         |<-- Return Asset DTO (No internal path)|                                         |
         |                                       |                                         |
         | --- GET /api/v1/assets/{id}/download->| -- Validate Owner Permission ----------->|
         |<-- Stream Physical File --------------|<-- Read File Stream --------------------|
```

### DAMS Core APIs (`/api/v1/assets`)
- `POST   /api/v1/assets/upload` - Multipart upload with SHA256 checksum & MIME classification.
- `GET    /api/v1/assets/{id}/download` - Secure file stream download for authorized owner.
- `GET    /api/v1/assets` - Paginated asset listing with type/status/favorite filters.
- `GET    /api/v1/assets/statistics` - Storage consumption and asset aggregations.
- `GET    /api/v1/assets/{id}` - Fetch single asset metadata.
- `PATCH  /api/v1/assets/{id}` - Rename asset or update description.
- `POST   /api/v1/assets/{id}/favorite` - Toggle asset favorite status.
- `DELETE /api/v1/assets/{id}` - Soft delete asset (move to trash).
- `POST   /api/v1/assets/{id}/restore` - Restore soft-deleted asset.

---

## 🔐 Authentication & Session Security Architecture

NeuroDesk AI uses a dual-token architecture (Access Token + Refresh Token with Token Rotation):

### Authentication Endpoints
- `POST /api/v1/auth/register` - Create new user account with bcrypt password hashing.
- `POST /api/v1/auth/login` - Authenticate credentials and issue Access & Refresh tokens.
- `POST /api/v1/auth/refresh` - Rotate refresh token and issue new token pair.
- `POST /api/v1/auth/logout` - Revoke refresh token session.
- `GET  /api/v1/users/me` - Fetch authenticated user details.
- `PUT  /api/v1/users/profile` - Update user display profile.
- `POST /api/v1/users/change-password` - Change password and revoke active sessions.
- `DELETE /api/v1/users/delete-account` - Soft delete account and revoke all sessions.

---

## 🛠 Technology Stack

### Frontend Architecture
- **Core Framework**: React 18+ powered by Vite
- **Styling & Icons**: Vanilla CSS & Tailwind CSS with dark theme aesthetics, Lucide React icons
- **State Management**: React Context (`AuthContext`, `AssetContext`, `ThemeContext`)
- **HTTP Client**: Axios with automatic Bearer token injection and 401 token-refresh interceptors

### Backend Architecture
- **API Framework**: FastAPI 0.111+ with async endpoints
- **Database ORM**: SQLAlchemy 2.0 with generic dialect-agnostic types
- **Storage Layer**: Pluggable `StorageService` with `LocalStorageProvider`
- **Validation**: Pydantic v2 schemas (`ConfigDict`)
- **Security**: Native `bcrypt` password hashing, PyJWT, SHA-256 token hashing

---

## 🚀 Quick Start Guide

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/githubriyaz1/NeuroDesk-AI.git
   cd NeuroDesk-AI
   ```

2. Run local setup script or launch dev environment:
   ```bash
   # Powershell script launches backend & frontend
   .\scripts\start-dev.ps1
   ```

3. Backend Pytest Execution:
   ```bash
   cd backend
   .\venv\Scripts\activate
   pytest -v
   ```

4. Frontend Build & Vitest Execution:
   ```bash
   cd frontend
   npm run build
   npm run test:run
   ```
