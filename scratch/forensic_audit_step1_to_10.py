import asyncio
import io
import os
import sys
import httpx
import pypdf

sys.path.insert(0, os.path.abspath("backend"))

from app.core.config import settings
from app.core.llm.gemini_provider import GeminiProvider
from app.core.llm.mock_provider import MockProvider
from app.core.llm.base import ProviderRequest
from app.core.routing.intent_router import intent_router, QueryIntent

BASE_URL = "http://localhost:8000/api/v1"

async def run_forensic_audit():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🔍 NEURODESK AI — GEMINI / PDF PIPELINE FORENSIC AUDIT")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # STEP 1 — VERIFY THE GEMINI API KEY
    # -------------------------------------------------------------------------
    print("\n--- STEP 1: VERIFY GEMINI API KEY & HEALTH ---")
    env_google_key = os.getenv("GOOGLE_API_KEY")
    env_gemini_key = os.getenv("GEMINI_API_KEY")
    cfg_google_key = getattr(settings, "GOOGLE_API_KEY", "")
    cfg_gemini_key = getattr(settings, "GEMINI_API_KEY", "")

    has_key = bool(env_google_key or env_gemini_key or cfg_google_key or cfg_gemini_key)
    print(f"Key Configured: {'YES' if has_key else 'NO'}")
    print(f"os.getenv('GOOGLE_API_KEY') present: {bool(env_google_key)}")
    print(f"os.getenv('GEMINI_API_KEY') present: {bool(env_gemini_key)}")
    print(f"settings.GOOGLE_API_KEY present: {bool(cfg_google_key)}")
    print(f"settings.GEMINI_API_KEY present: {bool(cfg_gemini_key)}")
    
    if env_google_key:
        precedence = "os.getenv('GOOGLE_API_KEY')"
    elif env_gemini_key:
        precedence = "os.getenv('GEMINI_API_KEY')"
    elif cfg_google_key:
        precedence = "settings.GOOGLE_API_KEY"
    elif cfg_gemini_key:
        precedence = "settings.GEMINI_API_KEY"
    else:
        precedence = "NONE (Key Missing)"
    print(f"Precedence active source: {precedence}")
    print(f"LLM_PROVIDER setting: {getattr(settings, 'LLM_PROVIDER', 'not set')}")
    print(f"LLM_MODEL setting: {getattr(settings, 'LLM_MODEL', 'not set')}")

    gemini_prov = GeminiProvider()
    print(f"GeminiProvider client initialized: {bool(gemini_prov._client)}")
    print(f"GeminiProvider health_check: {await gemini_prov.health_check()}")

    if gemini_prov._client:
        try:
            req = ProviderRequest(prompt="Return exactly: GEMINI_HEALTH_OK")
            res = await gemini_prov.generate_response(req)
            print(f"Live Gemini Health Request Result: status=SUCCESS, model={res.model}, provider={res.provider_name}, content_preview={res.content[:50]!r}")
            if "GEMINI_HEALTH_OK" in res.content:
                print("✅ LIVE GEMINI API TEST PASSED (Returned GEMINI_HEALTH_OK)")
            else:
                print(f"⚠️ Live Gemini API test returned unexpected content: {res.content[:100]!r}")
        except Exception as e:
            print(f"❌ LIVE GEMINI API TEST FAILED WITH EXCEPTION: {e}")
    else:
        print("❌ Cannot perform live Gemini API test: client not initialized (missing API key).")

    # -------------------------------------------------------------------------
    # STEP 2 — PROVE WHICH PROVIDER IS ACTUALLY USED FOR CHAT
    # -------------------------------------------------------------------------
    print("\n--- STEP 2: PROVE PROVIDER SELECTION IN CHAT ---")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        email = "audit_forensic_user3@neurodesk.ai"
        pw = "ForensicPass2026!"
        await client.post("/auth/register", json={"email": email, "full_name": "Auditor", "password": pw})
        login_res = await client.post("/auth/login", json={"email": email, "password": pw})
        token = login_res.json().get("access_token", "")
        headers = {"Authorization": f"Bearer {token}"}

        conv_res = await client.post("/chat/conversations", headers=headers, json={"title": "Forensic Audit Conversation"})
        conv_data = conv_res.json()
        conv_id = conv_data["id"]
        print(f"Created Conversation [{conv_id}]")
        print(f"Conversation settings_json: {conv_data.get('settings_json')}")
        print(f"Conversation provider_info_json: {conv_data.get('provider_info_json')}")

        prov_info = conv_data.get("provider_info_json") or {}
        selected_prov = prov_info.get("provider") or getattr(settings, "LLM_PROVIDER", "mock")
        print(f"PROVIDER_SELECTED in chat.py: '{selected_prov}'")

    # -------------------------------------------------------------------------
    # STEP 3 & 4 — PDF RETRIEVAL & CONTENT VERIFICATION
    # -------------------------------------------------------------------------
    print("\n--- STEP 3 & 4: TRACE PDF RETRIEVAL & CONTENT VERIFICATION ---")
    spec_pdf_paths = [
        "Architecture_Spec.pdf",
        "backend/Architecture_Spec.pdf",
        "storage/uploads/Architecture_Spec.pdf"
    ]
    found_pdf = None
    for p in spec_pdf_paths:
        if os.path.exists(p):
            found_pdf = p
            break
    
    print(f"Looking for Architecture_Spec.pdf... Found: {found_pdf}")
    if found_pdf:
        reader = pypdf.PdfReader(found_pdf)
        print(f"ACTUAL_PDF_PAGES: {len(reader.pages)}")
        page1_text = reader.pages[0].extract_text() if len(reader.pages) > 0 else ""
        print(f"ACTUAL_PDF_PAGE_1_TEXT (length={len(page1_text)}): {page1_text[:200]!r}")

    intent, conf, retrievers = intent_router.classify_intent("Explain this PDF", attached_asset_types=["pdf"])
    print(f"Intent Classification for 'Explain this PDF': intent={intent.value}, confidence={conf}, retrievers={retrievers}")

    # -------------------------------------------------------------------------
    # STEP 7 — CHECK FOR MOCK PROVIDER CONTAMINATION
    # -------------------------------------------------------------------------
    print("\n--- STEP 7: CHECK MOCK PROVIDER CONTAMINATION ---")
    mock_prov = MockProvider()
    test_req = ProviderRequest(
        prompt="Explain this PDF",
        system_prompt="[Enterprise Knowledge Engine Retracted Sources]:\nPDF Document 'Architecture_Spec.pdf' [Page 1]:\nSystem Architecture details..."
    )
    mock_res = await mock_prov.generate_response(test_req)
    print(f"MockProvider output preview for 'Explain this PDF':\n{mock_res.content[:300]}")

    print("\n=" * 80)
    print("END OF FORENSIC INSPECTION")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_forensic_audit())
