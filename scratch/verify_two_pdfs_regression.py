import asyncio
import io
import sys
import httpx

BASE_URL = "http://localhost:8005/api/v1"


def make_pdf(filename: str, title: str, text: str) -> bytes:
    """Helper to generate a valid PDF with pypdf extractable text."""
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


async def run_two_pdf_regression():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🚀 NEURODESK AI — 2-PDF REGRESSION & GROUNDING VERIFICATION AUDIT")
    print("=" * 80)

    audit_results = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Register & Login
        email = "twopdf_auditor_1000@neurodesk.ai"
        pw = "AuditPass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "TwoPDF Auditor", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create PDF A (Employee Handbook)
        pdf_a_bytes = make_pdf(
            "Employee_Handbook.pdf",
            "Employee Leave Policy Document",
            "Employee leave policy allows 24 days per year. Special keyword: EMPLOYEE_POLICY_1122."
        )
        up_a = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Employee_Handbook.pdf", io.BytesIO(pdf_a_bytes), "application/pdf")},
        )
        pdf_a_id = up_a.json()["id"]

        # 3. Create PDF B (Rocket Engineering Report)
        pdf_b_bytes = make_pdf(
            "Rocket_Engineering_Report.pdf",
            "Rocket Propulsion Engine Test Report",
            "Rocket engine test duration was 87 seconds. Special keyword: ROCKET_TEST_3344."
        )
        up_b = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Rocket_Engineering_Report.pdf", io.BytesIO(pdf_b_bytes), "application/pdf")},
        )
        pdf_b_id = up_b.json()["id"]

        # 4. Create PDF C (Riyaz Test Document)
        pdf_c_bytes = make_pdf(
            "Riyaz_Test_Document.pdf",
            "Riyaz Test Document TestCorp",
            "TestCorp Quantum Banana Revenue 987654321 Employees 42 Location Chennai NEURODESK_UNIQUE_84729."
        )
        up_c = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Riyaz_Test_Document.pdf", io.BytesIO(pdf_c_bytes), "application/pdf")},
        )
        pdf_c_id = up_c.json()["id"]

        # 5. Create CSV Asset
        csv_bytes = b"EmployeeID,Name,Age,Department,Salary\n1,Alice,30,Engineering,95000\n2,Bob,40,Sales,85000\n3,Charlie,50,HR,75000\n4,David,30,Engineering,105000\n"
        up_csv = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Employee.csv", io.BytesIO(csv_bytes), "text/csv")},
        )
        csv_id = up_csv.json()["id"]

        # --- TEST 1: PDF A (Employee Handbook) ---
        conv1 = await client.post("/chat/conversations", headers=headers, json={"title": "PDF A Test"})
        conv1_id = conv1.json()["id"]

        res1 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv1_id, "prompt": "Explain this pdf", "attached_assets": [pdf_a_id]},
        )
        text1 = res1.text
        print(f"\n--- RESPONSE FOR PDF A (Employee Handbook) ---\n{text1}")

        canned_frag = "System Design & Multi-Tenant Architecture"
        is_canned1 = canned_frag in text1
        has_pdf_a_kw = "EMPLOYEE_POLICY_1122" in text1 or "24 days" in text1 or "Employee" in text1
        has_pdf_b_kw1 = "ROCKET_TEST_3344" in text1 or "87 seconds" in text1

        audit_results["pdf_a_canned"] = is_canned1
        audit_results["pdf_a_grounded"] = has_pdf_a_kw and not has_pdf_b_kw1

        # --- TEST 2: PDF B (Rocket Engineering Report) ---
        conv2 = await client.post("/chat/conversations", headers=headers, json={"title": "PDF B Test"})
        conv2_id = conv2.json()["id"]

        res2 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv2_id, "prompt": "Explain this pdf", "attached_assets": [pdf_b_id]},
        )
        text2 = res2.text
        print(f"\n--- RESPONSE FOR PDF B (Rocket Engineering Report) ---\n{text2}")

        is_canned2 = canned_frag in text2
        has_pdf_b_kw2 = "ROCKET_TEST_3344" in text2 or "87 seconds" in text2 or "Rocket" in text2
        has_pdf_a_kw2 = "EMPLOYEE_POLICY_1122" in text2 or "24 days" in text2

        audit_results["pdf_b_canned"] = is_canned2
        audit_results["pdf_b_grounded"] = has_pdf_b_kw2 and not has_pdf_a_kw2

        # Check PDF A vs PDF B response difference
        audit_results["different_pdfs_different_responses"] = text1 != text2

        # --- TEST 3: PDF C (Riyaz Test Document with Unique Keyword) ---
        conv3 = await client.post("/chat/conversations", headers=headers, json={"title": "PDF C Test"})
        conv3_id = conv3.json()["id"]

        res3 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv3_id, "prompt": "Explain this pdf", "attached_assets": [pdf_c_id]},
        )
        text3 = res3.text
        print(f"\n--- RESPONSE FOR PDF C (Riyaz Test Document) ---\n{text3}")

        has_pdf_c_kw = "NEURODESK_UNIQUE_84729" in text3 or "TestCorp" in text3 or "Quantum" in text3 or "Chennai" in text3
        audit_results["pdf_c_unique_keyword_grounded"] = has_pdf_c_kw

        # --- TEST 4: PDF A + CSV Dual Asset Test ---
        conv4 = await client.post("/chat/conversations", headers=headers, json={"title": "PDF + CSV Test"})
        conv4_id = conv4.json()["id"]

        res4_pdf = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv4_id, "prompt": "Explain this pdf", "attached_assets": [pdf_a_id, csv_id]},
        )
        text4_pdf = res4_pdf.text
        print(f"\n--- DUAL ASSET TEST: 'Explain this pdf' ---\n{text4_pdf}")

        res4_csv = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv4_id, "prompt": "How many employees are there?", "attached_assets": [pdf_a_id, csv_id]},
        )
        text4_csv = res4_csv.text
        print(f"\n--- DUAL ASSET TEST: 'How many employees are there?' ---\n{text4_csv}")

        audit_results["dual_asset_pdf_query_used_pdf"] = "Employee" in text4_pdf or "24" in text4_pdf
        audit_results["dual_asset_csv_query_used_pandas"] = "4" in text4_csv or "rows" in text4_csv

        # --- TEST 5: Context Bleed / Memory Isolation Test ---
        # Query PDF B in conv1 (which previously queried PDF A)
        res_bleed = await client.post(
            "/chat/stream",
            headers=headers,
            json={"conversation_id": conv1_id, "prompt": "Explain this pdf", "attached_assets": [pdf_b_id]},
        )
        text_bleed = res_bleed.text
        print(f"\n--- CONTEXT ISOLATION TEST (Swapped attached asset in same conv) ---\n{text_bleed}")

        has_bleed_kw = "ROCKET_TEST_3344" in text_bleed or "87 seconds" in text_bleed or "Rocket" in text_bleed
        audit_results["memory_isolation_swapped_asset_grounded"] = has_bleed_kw

    print("\n=" * 80)
    print("📋 AUDIT SUMMARY REPORT:")
    for k, v in audit_results.items():
        print(f"  - {k}: {v}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_two_pdf_regression())
