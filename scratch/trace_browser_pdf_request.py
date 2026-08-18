import asyncio
import io
import sys
import httpx

BASE_URL = "http://localhost:8005/api/v1"


def make_pdf(title: str, text: str) -> bytes:
    """Helper to generate a valid PDF."""
    try:
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        c.drawString(72, 750, title)
        c.drawString(72, 700, text)
        c.save()
        return buf.getvalue()
    except Exception:
        stream_content = f"BT /F1 12 Tf 72 712 Td ({title}) Tj ET\nBT /F1 12 Tf 72 690 Td ({text}) Tj ET\n"
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


async def trace_browser_pdf_flow():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🔍 FORENSIC TRACE: BROWSER PDF UPLOAD & CHAT REQUEST PIPELINE")
    print("=" * 80)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Register & Login User
        email = "browser_tracer_5000@neurodesk.ai"
        pw = "BrowserPass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "Browser Tracer", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload PDF via Browser Upload Endpoint (POST /api/v1/assets/upload)
        pdf_bytes = make_pdf(
            "Browser Uploaded Document",
            "This is a browser uploaded PDF containing unique token BROWSER_PDF_TOKEN_9988."
        )
        up_res = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Browser_Uploaded_Doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        asset_data = up_res.json()
        asset_id = asset_data["id"]
        print(f"\n[PHASE 1 - UPLOAD]")
        print(f"  - Filename: {asset_data.get('original_filename') or asset_data.get('name')}")
        print(f"  - Asset ID: {asset_id}")
        print(f"  - Storage Path: {asset_data.get('storage_path')}")
        print(f"  - File Size: {asset_data.get('file_size')} bytes")

        # 3. Create Conversation
        conv = await client.post("/chat/conversations", headers=headers, json={"title": "Browser Chat Trace"})
        conv_id = conv.json()["id"]

        # 4. Simulate EXACT Browser Frontend Request A (attached_assets: [])
        print("\n[PHASE 2 - CHAT REQUEST A: attached_assets = [] (Default Browser Payload)]")
        payload_empty = {"conversation_id": conv_id, "prompt": "What is this PDF about?", "attached_assets": []}
        print(f"  - Payload sent: {payload_empty}")

        res_empty = await client.post("/chat/stream", headers=headers, json=payload_empty)
        text_empty = res_empty.text
        print(f"  - Response received:\n{text_empty}")

        # 5. Simulate Browser Frontend Request B (attached_assets: [asset_id])
        print("\n[PHASE 2 - CHAT REQUEST B: attached_assets = [asset_id] (With Asset ID)]")
        payload_with_id = {"conversation_id": conv_id, "prompt": "What is this PDF about?", "attached_assets": [asset_id]}
        print(f"  - Payload sent: {payload_with_id}")

        res_with_id = await client.post("/chat/stream", headers=headers, json=payload_with_id)
        text_with_id = res_with_id.text
        print(f"  - Response received:\n{text_with_id}")

    print("\n=" * 80)
    print("📋 TRACE SUMMARY COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(trace_browser_pdf_flow())
