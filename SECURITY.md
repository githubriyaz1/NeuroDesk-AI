# NeuroDesk AI — Security Architecture & Threat Model

## Overview

NeuroDesk AI is built around a defense-in-depth security model covering API authentication, server-side multi-tenant authorization, isolated code sandboxing, SSRF defense, and secret protection.

---

## 1. Authentication & JWT Tokens

- **Algorithm**: HMAC-SHA256 (HS256) signing (`utils/security.py`).
- **Token Expiry**: Short-lived access tokens (30 minutes) + refresh tokens (7 days).
- **Password Hashing**: Bcrypt with salted rounds.
- **Header Structure**: `Authorization: Bearer <JWT_ACCESS_TOKEN>`.

---

## 2. Server-Side Multi-Tenant Authorization (IDOR Protection)

All database queries across Workflows, Workflow Executions, Conversations, Messages, Assets, and Blueprints enforce `owner_id == current_user.id`.

- **Strict HTTP 404 Response**: Unauthorized access attempts by User B on User A's resources explicitly return **HTTP 404 Not Found** (rather than 403 Forbidden) to avoid revealing the existence of resources to unauthorized callers.

---

## 3. Python Sandbox Security (`python_sandbox.py`)

### AST Security Visitor (`ASTSecurityVisitor`)
Pre-audits code AST before spawning subprocesses.

- **Forbidden Modules**: `os`, `sys`, `subprocess`, `socket`, `shutil`, `ctypes`, `urllib`, `requests`, `httpx`, `tempfile`, etc.
- **Forbidden Calls**: `exec`, `eval`, `__import__`, `open`, `input`, `globals`, `locals`, `getattr`, `setattr`.
- **Forbidden Attributes**: `__builtins__`, `__globals__`, `__subclasses__`, `__code__`.

### Subprocess Isolation
- Executes inside isolated subprocesses (`asyncio.create_subprocess_exec`).
- Environment variables stripped of sensitive secrets (`safe_env`).
- Enforces a 5.0-second execution timeout.

> **Honest Security Boundary Note**: CPU cgroup caps and RAM limits rely on host OS or container configuration (Docker).

---

## 4. HTTP / SSRF Defense Engine (`http_executor.py`)

- **Protocol Restriction**: Accepts `http` and `https` protocols only.
- **DNS Resolution Audit**: Resolves hostnames via `socket.getaddrinfo` prior to initiating HTTP requests.
- **IP Blocklist**: Rejects loopback (`127.0.0.1`, `localhost`, `::1`), cloud metadata (`169.254.169.254`), and private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- **Limits**: Maximum 2 MB payload size limit, 10.0s timeout limit, and `follow_redirects=False` to prevent redirect bypasses.

---

## 5. Secrets Protection & Input Validation

- **Environment File**: `.env` is explicitly listed in `.gitignore`.
- **Zero API Key Leakage**: API response payloads, logs, and diagnostics NEVER return internal API keys or secrets.
- **Input Validation**: Pydantic schemas enforce type safety and character limits on all incoming JSON payloads.
