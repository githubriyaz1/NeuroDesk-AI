import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_conversation_lifecycle_and_messages(async_client: AsyncClient, auth_headers: dict):
    # 1. Create Conversation
    create_res = await async_client.post(
        "/api/v1/chat/conversations",
        headers=auth_headers,
        json={"title": "Data Analysis Project", "description": "Analyzing Q3 reports"},
    )
    assert create_res.status_code == 201
    conv_data = create_res.json()
    conv_id = conv_data["id"]
    assert conv_data["title"] == "Data Analysis Project"
    assert conv_data["is_pinned"] is False

    # 2. List Conversations
    list_res = await async_client.get("/api/v1/chat/conversations", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 3. Post Message & Trigger LLM Mock Response
    msg_res = await async_client.post(
        "/api/v1/chat/messages",
        headers=auth_headers,
        json={"conversation_id": conv_id, "prompt": "Can you write a Python script to analyze CSV data?"},
    )
    assert msg_res.status_code == 201
    assistant_msg = msg_res.json()
    assert assistant_msg["role"] == "assistant"
    assert "Python" in assistant_msg["content"] or "script" in assistant_msg["content"]
    assert assistant_msg["token_usage"]["total_tokens"] > 0

    # 4. Get Conversation Messages
    msgs_res = await async_client.get(f"/api/v1/chat/messages/{conv_id}", headers=auth_headers)
    assert msgs_res.status_code == 200
    messages = msgs_res.json()["messages"]
    assert len(messages) == 2  # 1 User + 1 Assistant

    # 5. Toggle Pin, Favorite, Archive
    pin_res = await async_client.post(f"/api/v1/chat/conversations/{conv_id}/pin", headers=auth_headers)
    assert pin_res.status_code == 200
    assert pin_res.json()["is_pinned"] is True

    fav_res = await async_client.post(f"/api/v1/chat/conversations/{conv_id}/favorite", headers=auth_headers)
    assert fav_res.status_code == 200
    assert fav_res.json()["is_favorite"] is True

    # 6. Duplicate Conversation
    dup_res = await async_client.post(f"/api/v1/chat/conversations/{conv_id}/duplicate", headers=auth_headers)
    assert dup_res.status_code == 201
    dup_data = dup_res.json()
    assert "(Copy)" in dup_data["title"]

    # 7. Export Conversation
    export_res = await async_client.get(f"/api/v1/chat/conversations/{conv_id}/export?format=markdown", headers=auth_headers)
    assert export_res.status_code == 200
    assert "Data Analysis Project" in export_res.json()["content"]

    # 8. Clear Conversation Messages
    clear_res = await async_client.post(f"/api/v1/chat/conversations/{conv_id}/clear", headers=auth_headers)
    assert clear_res.status_code == 200
    assert clear_res.json()["message_count"] == 0

    # 9. Delete Conversation
    del_res = await async_client.delete(f"/api/v1/chat/conversations/{conv_id}", headers=auth_headers)
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_conversation_import(async_client: AsyncClient, auth_headers: dict):
    import_payload = {
        "json_content": {
            "title": "Imported Financial Audit",
            "description": "JSON backup",
            "messages": [
                {"role": "user", "content": "What is net profit?"},
                {"role": "assistant", "content": "Net profit is revenue minus expenses."},
            ],
        }
    }
    import_res = await async_client.post("/api/v1/chat/conversations/import", headers=auth_headers, json=import_payload)
    assert import_res.status_code == 201
    imported_data = import_res.json()
    assert imported_data["title"] == "Imported Financial Audit"
    assert len(imported_data["messages"]) == 2
