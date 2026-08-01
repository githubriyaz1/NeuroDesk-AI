# NeuroDesk AI 🧠⚡

> Enterprise AI-Powered Intelligent Workspace for Data Analysis, AI Studio Modeling, Automated Workflows, Digital Asset Management (DAMS), Enterprise Asset Explorer, Universal Preview Engine (UPE), Metadata & Indexing Engine, and AI-Assisted Project Architecture.

[![CI/CD Pipeline](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/NeuroDesk-AI/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg?style=flat&logo=react)](https://reactjs.org)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![JWT Auth](https://img.shields.io/badge/Auth-JWT%20%2B%20Rotation-indigo.svg?style=flat&logo=json-web-tokens)](https://jwt.io)
[![Metadata Engine](https://img.shields.io/badge/Metadata-Indexing%20Engine-orange.svg?style=flat&logo=database)](https://jwt.io)
[![DAMS Core](https://img.shields.io/badge/Storage-DAMS%20Core-emerald.svg?style=flat&logo=files)](https://jwt.io)
[![UPE Engine](https://img.shields.io/badge/Preview-UPE%20Engine-purple.svg?style=flat&logo=eye)](https://jwt.io)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg?style=flat&logo=docker)](https://www.docker.com)

---

## 📌 Executive Overview

**NeuroDesk AI** is an enterprise-grade intelligent workspace designed to unify digital asset management, machine learning lifecycle management, metadata extraction & indexing, conversational AI analytics, automated pipeline orchestration, universal file previews, enterprise asset exploration, and AI-driven software project blueprinting into a single sleek interface.

---

## 🔍 Metadata & Indexing Engine (Sprint 3.4 Architecture)

The **Metadata & Indexing Engine** automatically extracts, indexes, stores, and refreshes format-specific metadata for digital assets upon upload or on-demand refresh.

```
+-------------------+                    +-----------------------+                    +---------------------------+
|   React Client    |                    | FastAPI Router        |                    |  Metadata Engine Layers   |
+---------+---------+                    +-----------+-----------+                    +-------------+-------------+
          |                                          |                                              |
          | --- GET /assets/{id}/metadata ---------->| -- Validate Owner & Call MetadataService --->|
          |                                          | -- MetadataIndexer selects Extractor ------->| (PDF/CSV/Excel/Image)
          |                                          | -- Persists to AssetMetadata DB Model ------>|
          |<-- Returns Categorized Metadata Groups --|                                              |
          |                                          |                                              |
          | --- POST /assets/{id}/metadata/refresh ->| -- Forces re-extraction & DB upsert -------->|
```

### Format-Specific Metadata Support
- **PDF**: Title, Author, Producer, Page Count, Encrypted flag, File Size.
- **CSV**: Row Count, Column Count, Headers JSON, Delimiter, Encoding.
- **Excel**: Sheet Count, Sheet Names JSON, Active Sheet Title.
- **Image**: Width, Height, Aspect Ratio, DPI, Color Mode, Image Format.
- **Fallback**: File Name, MIME Type, Extension, File Size.

### Metadata Engine REST APIs (`/api/v1/assets`)
- `GET  /api/v1/assets/{asset_id}/metadata` - Retrieves structured metadata grouped by logical categories.
- `POST /api/v1/assets/{asset_id}/metadata/refresh` - Forces re-extraction and refresh of asset metadata.

---

## 📂 Enterprise Asset Explorer (Sprint 3.3 Architecture)

The **Enterprise Asset Explorer** provides a Vercel/Linear-grade workspace experience for browsing, managing, and operating on digital assets.

### Asset Explorer REST APIs (`/api/v1/assets`)
- `POST   /api/v1/assets/bulk-action` - Execute bulk operations (delete, restore, favorite, unfavorite, archive, unarchive) across asset IDs.
- `POST   /api/v1/assets/{id}/archive` - Toggle asset archive state (`status: ARCHIVED`).
- `POST   /api/v1/assets/upload` - Multipart upload with SHA256 checksum & MIME classification.
- `GET    /api/v1/assets/{id}/download` - Secure file stream download for authorized owner.
- `GET    /api/v1/assets` - Paginated asset listing with flexible sorting & category filters.

---

## 👁️ Universal Preview Engine (UPE Architecture)

The **Universal Preview Engine (UPE)** establishes a unified, provider-based preview layer (`PreviewService` $\rightarrow$ `PDFPreviewProvider`, `CSVPreviewProvider`, `ExcelPreviewProvider`, `ImagePreviewProvider`, `UnsupportedPreviewProvider`) consumed across all workspace features.

---

## 🚀 Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Test Suites
```bash
# Backend pytest suite (27 tests)
cd backend && pytest -v

# Frontend Vitest runner (10 tests)
cd frontend && npm run test:run
```
