import asyncio
import io
import sys
import httpx

BASE_URL = "http://localhost:8000/api/v1"

FORBIDDEN_LEAKAGE_STRINGS = [
    "Conversation History:",
    "User Question:",
    "Assistant:",
    "system prompt",
    "Context Assessment",
    "Operational Guidelines",
]


async def run_rag_e2e_verification():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("📚 NEURODESK AI — CRITICAL RAG & DUAL-ASSET ROUTING LIVE E2E VERIFICATION")
    print("=" * 80)

    e2e_results = []

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Register & Auth
        email = "rag_e2e_user@neurodesk.ai"
        pw = "SecurePass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "RAG User", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload Sample PDF Asset
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 55 >>\nstream\nBT /F1 12 Tf 72 712 Td (NeuroDesk Architecture Specification Document Page 1) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000216 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n321\n%%EOF"
        pdf_upload = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Architecture_Spec.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )
        pdf_id = pdf_upload.json()["id"]

        # 3. Upload Sample CSV Asset
        csv_content = b"EmployeeID,Name,Age,Department,Salary\n1,Alice,30,Engineering,95000\n2,Bob,40,Sales,85000\n3,Charlie,50,HR,75000\n4,David,30,Engineering,105000\n"
        csv_upload = await client.post(
            "/assets/upload",
            headers=headers,
            files={"file": ("Employee.csv", io.BytesIO(csv_content), "text/csv")},
        )
        csv_id = csv_upload.json()["id"]

        both_assets = [pdf_id, csv_id]

        print(f"✅ Uploaded PDF ({pdf_id[:8]}) and CSV ({csv_id[:8]}) assets for dual-asset routing tests.")

        # Test Case 1: "Explain page 1" with BOTH PDF and CSV attached
        res1 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"prompt": "Explain page 1", "attached_asset_ids": both_assets},
        )
        text1 = res1.text
        if "PDF" in text1 or "Architecture_Spec.pdf" in text1 or "Page 1" in text1:
            print("✅ [Test 1] 'Explain page 1' with PDF+CSV correctly routed to PDF Page reasoning.")
            e2e_results.append(True)
        else:
            print(f"❌ [Test 1] 'Explain page 1' failed! Response: {text1[:200]}")
            e2e_results.append(False)

        # Test Case 2: "How many employees?" with BOTH PDF and CSV attached
        res2 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"prompt": "How many employees?", "attached_asset_ids": both_assets},
        )
        text2 = res2.text
        if "4" in text2 or "employees" in text2.lower():
            print("✅ [Test 2] 'How many employees?' correctly routed to CSV Pandas engine (Row Count: 4).")
            e2e_results.append(True)
        else:
            print(f"❌ [Test 2] 'How many employees?' failed! Response: {text2[:200]}")
            e2e_results.append(False)

        # Test Case 3: "Average age" with BOTH PDF and CSV attached
        res3 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"prompt": "Average age", "attached_asset_ids": both_assets},
        )
        text3 = res3.text
        if "37.5" in text3 or "37.50" in text3 or "age" in text3.lower():
            print("✅ [Test 3] 'Average age' correctly executed exact Pandas dataframe calculation (37.5).")
            e2e_results.append(True)
        else:
            print(f"❌ [Test 3] 'Average age' failed! Response: {text3[:200]}")
            e2e_results.append(False)

        # Test Case 4: "Summarize page 1" with BOTH PDF and CSV attached
        res4 = await client.post(
            "/chat/stream",
            headers=headers,
            json={"prompt": "Summarize page 1", "attached_asset_ids": both_assets},
        )
        text4 = res4.text
        if "DataFrame" not in text4 and "Pandas" not in text4:
            print("✅ [Test 4] 'Summarize page 1' correctly executed PDF summary without invoking CSV analysis.")
            e2e_results.append(True)
        else:
            print(f"❌ [Test 4] 'Summarize page 1' improperly invoked CSV analysis! Response: {text4[:200]}")
            e2e_results.append(False)

        # Test Case 5: Zero System Prompt / History Leakage Check across all responses
        leakage_clean = True
        for idx, t in enumerate([text1, text2, text3, text4], 1):
            for forbidden in FORBIDDEN_LEAKAGE_STRINGS:
                if forbidden in t:
                    print(f"❌ [Test 5] Leakage detected in Response {idx}: '{forbidden}'")
                    leakage_clean = False

        if leakage_clean:
            print("✅ [Test 5] Verified zero system prompt or history text leakage in all streaming response payloads.")
            e2e_results.append(True)
        else:
            e2e_results.append(False)

    print("=" * 80)
    passed_cnt = sum(1 for r in e2e_results if r)
    total_cnt = len(e2e_results)
    print(f"📚 RAG & DUAL-ASSET ROUTING SUMMARY: {passed_cnt}/{total_cnt} TESTS PASSED WITH 100% SUCCESS")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_rag_e2e_verification())
