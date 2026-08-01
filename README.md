# NeuroDesk AI 🧠⚡

> Enterprise AI-Powered Intelligent Workspace for Data Analysis, AI Studio Modeling, Automated Workflows, and AI-Assisted Project Architecture.

[![CI/CD Pipeline](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?style=flat&logo=react)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![JWT Auth](https://img.shields.io/badge/Auth-JWT%20%2B%20Rotation-indigo.svg?style=flat&logo=json-web-tokens)](https://jwt.io)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg?style=flat&logo=docker)](https://www.docker.com)

---

## 📌 Executive Overview

**NeuroDesk AI** is an enterprise-grade intelligent workspace designed to unify data engineering, machine learning lifecycle management, conversational AI analytics, automated pipeline orchestration, and AI-driven software project blueprinting into a single sleek interface.

NeuroDesk AI incorporates a production-ready **JWT Authentication & Token Rotation Module** with secure bcrypt password hashing, persistent session tracking, automatic token refreshing, and fine-grained access control.

---

## 🔐 Authentication & Session Security Architecture

NeuroDesk AI uses a dual-token architecture (Access Token + Refresh Token with Token Rotation):

```
+------------------+                    +------------------+                    +------------------+
|   React Client   |                    | FastAPI Auth Gateway               | PostgreSQL Engine|
+--------+---------+                    +--------+---------+                    +--------+---------+
         |                                       |                                       |
         | --- POST /api/v1/auth/login --------->| -- Query User & verify bcrypt password ->|
         |                                       | <-- Return User Record ---------------|
         |<-- Return { access_token, refresh_tok}| -- Save Refresh Token SHA-256 Hash -->|
         |                                       |                                       |
         | --- HTTP Request (Bearer Access) ---->| -- Validate JWT Signature & Expire --->|
         |<-- HTTP 200 OK Response --------------|                                       |
         |                                       |                                       |
         | (Access Token Expired: HTTP 401)      |                                       |
         | --- POST /api/v1/auth/refresh ------->| -- Lookup Hash & verify not revoked ->|
         |                                       | -- Revoke Old Token & Issue New Token ->|
         |<-- Return New Token Pair -------------|                                       |
```

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
- **Routing**: React Router DOM v6 with `ProtectedRoute` guards
- **Authentication Context**: Global `AuthContext` with session hydration and automatic token refresh interceptor
- **HTTP Client**: Axios with centralized request/response token rotation interceptors
- **Styling**: Tailwind CSS v3 with modern dark design tokens & glassmorphism
- **Icons**: Lucide React
- **Unit Testing**: Vitest + React Testing Library

### Backend Architecture
- **Core API Engine**: Python 3.11+ & FastAPI
- **Security & Cryptography**: Passlib (bcrypt), PyJWT, Python `secrets` & `hashlib`
- **Data Validation & DTOs**: Pydantic v2 & Pydantic-Settings
- **ORM & Database Connection**: SQLAlchemy 2.0 Async ORM (`asyncpg`)
- **Logging & Monitoring**: Structured JSON/Console logging middleware with request timing
- **Unit Testing**: Pytest + HTTPX test suite

---

## 🚀 Getting Started

### Option A: Running with Docker (Recommended)
```bash
docker-compose up --build -d
```
Access points:
- **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option B: Running Local Tests
```bash
# Run backend pytest suite (Authentication & API tests)
cd backend
pytest -v

# Run frontend Vitest suite
cd frontend
npm run test:run
```

---

## 📄 License & Attribution

NeuroDesk AI is engineered following Enterprise Clean Architecture principles. Distributed under the MIT License.
