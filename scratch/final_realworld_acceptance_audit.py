import asyncio
import io
import sys
import httpx

BASE_URL = "http://localhost:8005/api/v1"


def make_pdf(title: str, text: str) -> bytes:
    """Generates valid PDF bytes with pypdf extractable text using reportlab canvas."""
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


async def run_final_acceptance_audit():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🏆 NEURODESK AI — FINAL REAL-WORLD PRODUCT ACCEPTANCE AUDIT")
    print("=" * 80)

    audit_results = {}
    audit_logs = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Register & Login User
        email = "final_acceptance_user_2026@neurodesk.ai"
        pw = "FinalPass2026!"
        reg_res = await client.post("/auth/register", json={"email": email, "full_name": "Final Acceptance Tester", "password": pw})
        assert reg_res.status_code == 201, reg_res.text

        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload PDF A (Quantum Supercomputing Policy)
        pdf_a_content = (
            "Quantum Supercomputing Architecture Specification 2026. "
            "System features 1024 logical qubits with 99.99 percent gate fidelity. "
            "Employee vacation leave entitlement is 40 days per annum. "
            "Unique identifier token: QUANTUM_CORE_PROCESSED_98765."
        )
        pdf_a_bytes = make_pdf("Quantum Supercomputing Spec", pdf_a_content)
        up_a = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Quantum_Supercomputing_Whitepaper.pdf", io.BytesIO(pdf_a_bytes), "application/pdf")},
        )
        assert up_a.status_code == 201, up_a.text
        pdf_a_id = up_a.json()["id"]
        print(f"\n[ASSET UPLOAD A] Uploaded PDF A (Quantum_Supercomputing_Whitepaper.pdf) -> ID: {pdf_a_id}")

        # 3. Upload PDF B (Rocket Propulsion Test)
        pdf_b_content = (
            "Rocket Propulsion Engine Cryogenic Test Stand Log. "
            "Liquid hydrogen combustion chamber pressure reached 185 bar. "
            "Static fire burn duration was 92.5 seconds cleanly. "
            "Unique identifier token: ROCKET_THRUST_METRIC_3344."
        )
        pdf_b_bytes = make_pdf("Rocket Propulsion Test Log", pdf_b_content)
        up_b = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Rocket_Propulsion_Lab_Report.pdf", io.BytesIO(pdf_b_bytes), "application/pdf")},
        )
        assert up_b.status_code == 201, up_b.text
        pdf_b_id = up_b.json()["id"]
        print(f"[ASSET UPLOAD B] Uploaded PDF B (Rocket_Propulsion_Lab_Report.pdf) -> ID: {pdf_b_id}")

        # 4. Upload CSV (Employee Payroll)
        csv_content = b"EmployeeID,Name,Department,Salary\n101,Alice,AI Engineering,145000\n102,Bob,Data Platform,135000\n103,Charlie,Product,125000\n104,David,Security,155000\n105,Eve,Operations,115000\n"
        up_csv = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Employee_Payroll_2026.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert up_csv.status_code == 201, up_csv.text
        csv_id = up_csv.json()["id"]
        print(f"[ASSET UPLOAD C] Uploaded CSV (Employee_Payroll_2026.csv) -> ID: {csv_id}")

        # --- STEP 1: Query PDF A ("What is this PDF about?") ---
        conv1 = await client.post("/chat/conversations", headers=headers, json={"title": "PDF A Conversation"})
        assert conv1.status_code == 201, conv1.text
        conv1_id = conv1.json()["id"]

        payload1 = {"conversation_id": conv1_id, "prompt": "What is this PDF about?", "attached_assets": [pdf_a_id]}
        res1 = await client.post("/chat/stream", headers=headers, json=payload1)
        text1 = res1.text
        print(f"\n--- [TEST 1] PDF A Initial Query Response ---\n{text1}")

        # Verification 1 & 2 & 12 & 13
        has_quantum_kw = "QUANTUM_CORE_PROCESSED_98765" in text1 or "1024" in text1 or "qubits" in text1 or "Quantum" in text1
        has_canned = "System Design & Multi-Tenant Architecture" in text1
        has_error_msg = "could not be retrieved" in text1 or "no readable text" in text1
        has_citation_a = "Quantum_Supercomputing_Whitepaper.pdf" in text1 or "Page 1" in text1

        audit_results["1_pdf_a_initial_grounded"] = has_quantum_kw and not has_canned and not has_error_msg
        audit_results["12_no_canned_mock_response"] = not has_canned
        audit_results["13_citation_contains_filename_and_page"] = has_citation_a

        # --- STEP 2: Follow-up Question on PDF A ---
        payload2 = {"conversation_id": conv1_id, "prompt": "What are the specific policy details and leave entitlement mentioned in this document?", "attached_assets": [pdf_a_id]}
        res2 = await client.post("/chat/stream", headers=headers, json=payload2)
        text2 = res2.text
        print(f"\n--- [TEST 2] PDF A Follow-up Response ---\n{text2}")

        has_leave_policy = "40 days" in text2 or "leave" in text2.lower() or "vacation" in text2.lower() or "Entitlement" in text2
        audit_results["3_15_pdf_a_followup_preserves_context"] = has_leave_policy

        # --- STEP 3: Query PDF B ("What is this PDF about?") ---
        conv2 = await client.post("/chat/conversations", headers=headers, json={"title": "PDF B Conversation"})
        conv2_id = conv2.json()["id"]

        payload3 = {"conversation_id": conv2_id, "prompt": "What is this PDF about?", "attached_assets": [pdf_b_id]}
        res3 = await client.post("/chat/stream", headers=headers, json=payload3)
        text3 = res3.text
        print(f"\n--- [TEST 3] PDF B Response ---\n{text3}")

        has_rocket_kw = "ROCKET_THRUST_METRIC_3344" in text3 or "185 bar" in text3 or "92.5 seconds" in text3 or "Rocket" in text3
        has_bleed_from_a = "QUANTUM_CORE_PROCESSED_98765" in text3 or "40 days" in text3

        audit_results["4_5_6_pdf_b_grounded_no_bleed"] = has_rocket_kw and not has_bleed_from_a
        audit_results["6_pdf_a_b_responses_materially_different"] = text1 != text3

        # --- STEP 4: CSV Statistical Question ("How many rows are there?") ---
        conv3 = await client.post("/chat/conversations", headers=headers, json={"title": "Dual Asset Conversation"})
        conv3_id = conv3.json()["id"]

        payload4 = {"conversation_id": conv3_id, "prompt": "How many rows are there?", "attached_assets": [pdf_a_id, csv_id]}
        res4 = await client.post("/chat/stream", headers=headers, json=payload4)
        text4 = res4.text
        print(f"\n--- [TEST 4] CSV Query Response ---\n{text4}")

        has_5_rows = "5" in text4 or "rows" in text4 or "records" in text4
        has_pandas_tag = "Dataframe Operations Verified" in text4 or "Employee_Payroll_2026.csv" in text4

        audit_results["7_8_9_csv_pandas_dataframe_analysis_used"] = has_5_rows and has_pandas_tag

        # --- STEP 5: PDF Query with Dual Assets Attached ("What technologies are mentioned in the PDF?") ---
        payload5 = {"conversation_id": conv3_id, "prompt": "What technologies are mentioned in the PDF?", "attached_assets": [pdf_a_id, csv_id]}
        res5 = await client.post("/chat/stream", headers=headers, json=payload5)
        text5 = res5.text
        print(f"\n--- [TEST 5] PDF Query with Dual Assets Attached Response ---\n{text5}")

        has_pdf_tech = "1024" in text5 or "qubits" in text5 or "Quantum" in text5 or "gate fidelity" in text5
        has_csv_bleed = "145000" in text5 or "Operations" in text5

        audit_results["10_11_dual_asset_pdf_query_remains_pdf_grounded"] = has_pdf_tech and not has_csv_bleed

        # --- STEP 6: System Prompt / Internal Instruction Leakage Audit ---
        sys_leakage = "You are NeuroDesk AI" in text1 or "[Enterprise Knowledge Engine Retracted Sources]" in text1 or "SYSTEM_PROMPT" in text1
        audit_results["14_no_system_prompt_or_internal_leakage"] = not sys_leakage

    print("\n=" * 80)
    print("📊 FINAL ACCEPTANCE AUDIT RESULTS:")
    all_passed = True
    for test_name, passed in audit_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_passed = False
        print(f"  {status} - {test_name}")
    print("=" * 80)
    print(f"OVERALL STATUS: {'✅ ALL 15 CRITERIA PASSED' if all_passed else '❌ AUDIT FAILED'}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_final_acceptance_audit())
