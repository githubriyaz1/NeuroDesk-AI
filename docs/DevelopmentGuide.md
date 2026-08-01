# NeuroDesk AI Developer Onboarding & Contribution Guide

## 1. Development Prerequisites

Ensure your environment has the following software installed:
- **Node.js**: v18.0.0 or higher
- **Python**: v3.11.0 or higher
- **PostgreSQL**: v14.0 or higher (or Docker)
- **Git**: v2.30.0 or higher

## 2. Authentication System Overview

### Endpoints
- `POST /api/v1/auth/register`: Creates a user record. Returns UserResponse.
- `POST /api/v1/auth/login`: Authenticates credentials. Returns TokenResponse `{ access_token, refresh_token, user }`.
- `POST /api/v1/auth/refresh`: Rotates refresh token and issues new token pair.
- `POST /api/v1/auth/logout`: Revokes refresh token.
- `GET  /api/v1/users/me`: Requires Bearer JWT. Returns current user details.
- `PUT  /api/v1/users/profile`: Requires Bearer JWT. Updates user full_name.
- `POST /api/v1/users/change-password`: Requires Bearer JWT. Verifies current password and updates hash.
- `DELETE /api/v1/users/delete-account`: Requires Bearer JWT. Soft deletes user account.

## 3. Running Backend Tests

The Pytest suite tests user registration, login, token refresh, duplicate email validation, protected routes, profile updates, password changes, and account deletion:

```bash
cd backend
venv\Scripts\activate
pytest -v
```

## 4. Running Frontend Tests & Build

```bash
cd frontend
npm run test:run
npm run build
```
