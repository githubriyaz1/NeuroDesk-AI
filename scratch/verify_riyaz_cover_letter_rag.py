import asyncio
import io
import sys
import httpx

BASE_URL = "http://localhost:8005/api/v1"


def make_pdf(title: str, text: str) -> bytes:
    """Helper to generate a valid PDF with pypdf extractable text using reportlab or clean stream."""
    try:
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        c.drawString(72, 750, title)
        words = text.split(" ")
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            if len(" ".join(curr)) > 60:
                lines.append(" ".join(curr))
                curr = []
        if curr:
            lines.append(" ".join(curr))
        y = 710
        for line in lines:
            c.drawString(72, y, line)
            y -= 20
        c.save()
        return buf.getvalue()
    except ImportError:
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


async def run_riyaz_cover_letter_audit():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🚀 NEURODESK AI — RIYAZ COVER LETTER SURGICAL RAG VERIFICATION")
    print("=" * 80)

    results = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Register & Login
        email = "riyaz_auditor_3000@neurodesk.ai"
        pw = "AuditPass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "Riyaz Auditor", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload "Riyaz cover letter(2).pdf"
        cover_letter_text = (
            "Mohamed Riyaz. B.Tech Information Technology, Francis Xavier Engineering College. "
            "Applying for internship at VDart. Skills: Python, JavaScript, React.js, Node.js, Express.js, MongoDB, MySQL, REST APIs, Git, GitHub. "
            "Eager to gain professional experience and contribute to VDart projects."
        )
        pdf_a_bytes = make_pdf("Mohamed Riyaz Cover Letter VDart", cover_letter_text)
        up_a = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Riyaz cover letter(2).pdf", io.BytesIO(pdf_a_bytes), "application/pdf")},
        )
        pdf_a_id = up_a.json()["id"]

        # 3. Upload Unrelated PDF B (Solar Physics Research)
        solar_text = "Solar flare intensity measure 9.4 Megawatts. Coronal mass ejection detected at observatory 4821."
        pdf_b_bytes = make_pdf("Solar Flare Physics Paper", solar_text)
        up_b = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Solar_Physics_Report.pdf", io.BytesIO(pdf_b_bytes), "application/pdf")},
        )
        pdf_b_id = up_b.json()["id"]

        # 4. Upload Employee.csv
        csv_bytes = b"EmployeeID,Name,Age,Department,Salary\n1,Alice,30,Engineering,95000\n2,Bob,40,Sales,85000\n3,Charlie,50,HR,75000\n4,David,30,Engineering,105000\n"
        up_csv = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Employee.csv", io.BytesIO(csv_bytes), "text/csv")},
        )
        csv_id = up_csv.json()["id"]

        # --- STEP 5: Test Query "What is the PDF explaining?" on Riyaz Cover Letter ---
        conv1 = await client.post("/chat/conversations", headers=headers, json={"title": "Riyaz Cover Letter Chat"})
        conv1_id = conv1.json()["id"]

        res1 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv1_id, "prompt": "What is the PDF explaining?", "attached_assets": [pdf_a_id]},
        )
        text1 = res1.text
        print(f"\n--- RESPONSE FOR 'Riyaz cover letter(2).pdf' ---\n{text1}")

        # Grounding Assertions for Riyaz Cover Letter
        has_riyaz = "Riyaz" in text1 or "Mohamed" in text1 or "VDart" in text1 or "cover letter" in text1.lower() or "internship" in text1.lower()
        has_skills = "Python" in text1 or "React" in text1 or "JavaScript" in text1 or "B.Tech" in text1 or "Information Technology" in text1
        has_canned = "System Design & Multi-Tenant Architecture" in text1 or "Architecture_Spec.pdf" in text1
        has_error_msg = "could not be retrieved" in text1 or "no readable text" in text1

        results["riyaz_pdf_grounded"] = (has_riyaz or has_skills) and not has_canned and not has_error_msg
        results["riyaz_pdf_citation_present"] = "Riyaz cover letter(2).pdf" in text1 or "Riyaz cover letter" in text1

        # --- STEP 6: Test Unrelated PDF B ---
        conv2 = await client.post("/chat/conversations", headers=headers, json={"title": "Solar Physics Chat"})
        conv2_id = conv2.json()["id"]

        res2 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv2_id, "prompt": "What is the PDF explaining?", "attached_assets": [pdf_b_id]},
        )
        text2 = res2.text
        print(f"\n--- RESPONSE FOR 'Solar_Physics_Report.pdf' ---\n{text2}")

        has_solar = "Solar" in text2 or "flare" in text2 or "Coronal" in text2 or "observatory" in text2 or "Megawatts" in text2
        results["pdf_b_solar_grounded"] = has_solar and not ("VDart" in text2 or "Riyaz" in text2)
        results["pdf_a_and_pdf_b_responses_different"] = text1 != text2

        # --- STEP 7: Test Dual Asset (PDF + CSV) Isolation ---
        conv3 = await client.post("/chat/conversations", headers=headers, json={"title": "Dual Asset Chat"})
        conv3_id = conv3.json()["id"]

        # 7a. "What is the PDF explaining?" with both assets attached
        res3_pdf = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv3_id, "prompt": "What is the PDF explaining?", "attached_assets": [pdf_a_id, csv_id]},
        )
        text3_pdf = res3_pdf.text
        print(f"\n--- DUAL ASSET: 'What is the PDF explaining?' ---\n{text3_pdf}")

        # 7b. "How many employees are there?" with both assets attached
        res3_csv = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv3_id, "prompt": "How many employees are there?", "attached_assets": [pdf_a_id, csv_id]},
        )
        text3_csv = res3_csv.text
        print(f"\n--- DUAL ASSET: 'How many employees are there?' ---\n{text3_csv}")

        # 7c. "What technologies are mentioned in the PDF?" with both assets attached
        res3_tech = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv3_id, "prompt": "What technologies are mentioned in the PDF?", "attached_assets": [pdf_a_id, csv_id]},
        )
        text3_tech = res3_tech.text
        print(f"\n--- DUAL ASSET: 'What technologies are mentioned in the PDF?' ---\n{text3_tech}")

        results["dual_asset_pdf_query_used_pdf"] = "Riyaz" in text3_pdf or "VDart" in text3_pdf or "cover letter" in text3_pdf.lower()
        results["dual_asset_csv_query_used_pandas"] = "4" in text3_csv or "rows" in text3_csv
        results["dual_asset_tech_query_mentioned_skills"] = "Python" in text3_tech or "React" in text3_tech or "JavaScript" in text3_tech or "B.Tech" in text3_tech

    print("\n=" * 80)
    print("📋 SURGICAL RAG AUDIT SUMMARY REPORT:")
    for k, v in results.items():
        print(f"  - {k}: {v}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_riyaz_cover_letter_audit())
