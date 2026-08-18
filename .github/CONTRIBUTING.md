# Contributing to NeuroDesk AI

Thank you for your interest in contributing to **NeuroDesk AI**!

## Development Setup

1. **Fork & Clone repository**:
   ```bash
   git clone https.github.com/your-username/NeuroDesk-AI.git
   cd NeuroDesk-AI
   ```

2. **One-Command Developer Setup**:
   ```bash
   # Windows PowerShell:
   .\dev.ps1 setup

   # Linux / macOS:
   ./dev.sh setup
   ```

3. **Running Local Environment**:
   ```bash
   # Terminal 1: FastAPI Backend
   .\dev.ps1 backend

   # Terminal 2: Vite React Frontend
   .\dev.ps1 frontend
   ```

4. **Running Automated Tests**:
   ```bash
   .\dev.ps1 test
   ```

## Code Quality & Guidelines

- Maintain strict layering (`Router` -> `Service` -> `Repository` -> `Database`).
- Enforce strict user isolation across all endpoints (`owner_id == current_user.id`).
- Run `ruff check app/` and `npm run lint` before creating pull requests.
