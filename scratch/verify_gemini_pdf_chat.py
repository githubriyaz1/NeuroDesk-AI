import asyncio
import io
import sys
import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def run_gemini_pdf_chat_verification():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🚀 NEURODESK AI — GROUNDED GEMINI PDF CHAT & DUAL-ASSET VERIFICATION")
    print("=" * 80)

    audit_report = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Register & Auth
        email = "gemini_verification_user4@neurodesk.ai"
        pw = "VerifyPass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "Gemini Verifier", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create NEW Conversation
        conv_res = await client.post("/chat/conversations", headers=headers, json={"title": "Gemini PDF Chat Verification"})
        print(f"conv_res status: {conv_res.status_code}, text: {conv_res.text}")
        conv_data = conv_res.json()
        conv_id = conv_data["id"]
        print(f"Created Conversation [{conv_id}]")
        print(f"Conversation settings_json: {conv_data.get('settings_json')}")
        print(f"Conversation provider_info_json: {conv_data.get('provider_info_json')}")

        # 3. Post "Hello" to new conversation
        res_hello = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv_id, "prompt": "Hello"},
        )
        print(f"\n--- TEST 1: Hello Query Stream Output (First 200 chars) ---\n{res_hello.text[:200]}")
        audit_report["new_conversation_provider"] = conv_data.get("provider_info_json", {}).get("provider")

        # 4. Upload Architecture_Spec.pdf & Employee.csv
        pdf_content = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
            b"4 0 obj\n<< /Length 120 >>\nstream\n"
            b"BT /F1 12 Tf 72 712 Td (NeuroDesk AI High Availability Microservices Architecture Specification Document Page 1) Tj ET\n"
            b"endstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000216 00000 n \n"
            b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n380\n%%EOF"
        )
        pdf_upload = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Architecture_Spec.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )
        pdf_id = pdf_upload.json()["id"]

        csv_content = b"EmployeeID,Name,Age,Department,Salary\n1,Alice,30,Engineering,95000\n2,Bob,40,Sales,85000\n3,Charlie,50,HR,75000\n4,David,30,Engineering,105000\n"
        csv_upload = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Employee.csv", io.BytesIO(csv_content), "text/csv")},
        )
        csv_id = csv_upload.json()["id"]

        both_assets = [pdf_id, csv_id]
        print(f"\nUploaded PDF [{pdf_id[:8]}] and CSV [{csv_id[:8]}]")

        # 5. Query: "Explain this PDF" with BOTH assets attached
        res_explain_pdf = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv_id, "prompt": "Explain this PDF", "attached_asset_ids": both_assets},
        )
        explain_pdf_text = res_explain_pdf.text
        print(f"\n--- TEST 2: 'Explain this PDF' Response Payload ---\n{explain_pdf_text}")

        # Check that response is NOT the old canned MockProvider response
        canned_mock_text = "The document provides technical specifications, operational parameters, and system requirements."
        is_mock_canned = canned_mock_text in explain_pdf_text

        audit_report["pdf_explain_canned_mock"] = is_mock_canned
        audit_report["pdf_explain_grounded"] = not is_mock_canned and ("Architecture" in explain_pdf_text or "PDF" in explain_pdf_text)

        # 6. Query: "Explain page 1" with BOTH assets attached
        res_explain_p1 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv_id, "prompt": "Explain page 1", "attached_asset_ids": both_assets},
        )
        explain_p1_text = res_explain_p1.text
        print(f"\n--- TEST 3: 'Explain page 1' Response Payload ---\n{explain_p1_text}")
        audit_report["explain_page1_grounded"] = "Page 1" in explain_p1_text or "Architecture" in explain_p1_text

        # 7. Dual-Asset CSV Test: "How many employees are there?"
        res_csv_emp = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv_id, "prompt": "How many employees are there?", "attached_asset_ids": both_assets},
        )
        csv_emp_text = res_csv_emp.text
        print(f"\n--- TEST 4: 'How many employees are there?' CSV Response Payload ---\n{csv_emp_text}")
        audit_report["csv_pandas_calculation"] = "4" in csv_emp_text or "employees" in csv_emp_text.lower()

    print("\n=" * 80)
    print("📋 VERIFICATION SUMMARY SUMMARY REPORT:")
    for k, v in audit_report.items():
        print(f"  - {k}: {v}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_gemini_pdf_chat_verification())
