import pytest
from uuid import uuid4
from httpx import AsyncClient
from app.main import app
import io


def make_test_pdf_bytes(title: str, text: str) -> bytes:
    """Generates valid PDF bytes for testing."""
    try:
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        c.drawString(72, 750, title)
        c.drawString(72, 700, text)
        c.save()
        return buf.getvalue()
    except Exception:
        clean_title = title.replace("(", "\\(").replace(")", "\\)")
        clean_text = text.replace("(", "\\(").replace(")", "\\)")
        stream_content = f"BT /F1 12 Tf 72 712 Td ({clean_title}) Tj ET\nBT /F1 12 Tf 72 690 Td ({clean_text}) Tj ET\n"
        stream_bytes = stream_content.encode("latin-1", "ignore")
        length = len(stream_bytes)
        pdf_text = (
            f"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            f"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
            f"4 0 obj\n<< /Length {length} >>\nstream\n"
            f"{stream_content}"
            f"endstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000216 00000 n \n"
            f"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n380\n%%EOF"
        )
        return pdf_text.encode("latin-1", "ignore")


@pytest.mark.anyio
async def test_browser_equivalent_pdf_upload_and_chat_rag():
    """Verifies that an asset uploaded via browser endpoint is correctly retrieved in chat even if attached_assets is empty."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Register & Login User
        email = f"test_browser_rag_{uuid4().hex[:8]}@neurodesk.ai"
        pw = "TestPass2026!"
        reg_res = await client.post("/api/v1/auth/register", json={"email": email, "full_name": "Browser RAG Tester", "password": pw})
        assert reg_res.status_code == 201, reg_res.text

        login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": pw})
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload PDF Asset
        pdf_bytes = make_test_pdf_bytes("Quantum Computing Manual", "Quantum computer qubit stability 99.9 percent. Keyword: QUBIT_PASS_4455.")
        up_res = await client.post(
            "/api/v1/assets/upload",
            headers=headers,
            files={"file": ("Quantum_Manual.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        assert up_res.status_code == 201, up_res.text
        asset_id = up_res.json()["id"]

        # 3. Create Conversation
        conv_res = await client.post("/api/v1/chat/conversations", headers=headers, json={"title": "Browser RAG Test"})
        assert conv_res.status_code == 201, conv_res.text
        conv_id = conv_res.json()["id"]

        # 4. Stream Chat with empty attached_assets (Browser default)
        stream_res = await client.post(
            "/api/v1/chat/stream",
            headers=headers,
            json={"conversation_id": conv_id, "prompt": "What is this PDF about?", "attached_assets": []},
        )
        assert stream_res.status_code == 200, stream_res.text
        body = stream_res.text
        assert "Quantum" in body or "qubit" in body or "QUBIT_PASS_4455" in body or "Quantum_Manual.pdf" in body
        assert "No workspace documents or PDF contexts have been provided" not in body

        # 5. Stream Chat with explicit attached_assets ID
        stream_res_explicit = await client.post(
            "/api/v1/chat/stream",
            headers=headers,
            json={"conversation_id": conv_id, "prompt": "What is this PDF about?", "attached_assets": [asset_id]},
        )
        assert stream_res_explicit.status_code == 200, stream_res_explicit.text
        body_explicit = stream_res_explicit.text
        assert "Quantum" in body_explicit or "qubit" in body_explicit or "QUBIT_PASS_4455" in body_explicit or "Quantum_Manual.pdf" in body_explicit
        assert "No workspace documents or PDF contexts have been provided" not in body_explicit
