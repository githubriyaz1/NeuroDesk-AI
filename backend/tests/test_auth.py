import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_success(async_client: AsyncClient):
    payload = {
        "email": "architect@neurodesk.ai",
        "full_name": "Principal Architect",
        "password": "SecurePassword2026!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert data["is_active"] is True
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(async_client: AsyncClient):
    payload = {
        "email": "duplicate@neurodesk.ai",
        "full_name": "Test User",
        "password": "SecurePassword2026!",
    }
    # First registration
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Duplicate registration
    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["message"]


@pytest.mark.asyncio
async def test_user_login_invalid_password(async_client: AsyncClient):
    reg_payload = {
        "email": "login_test@neurodesk.ai",
        "full_name": "Login User",
        "password": "CorrectPassword123!",
    }
    await async_client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "login_test@neurodesk.ai",
        "password": "WrongPassword123!",
    }
    response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_full_auth_lifecycle(async_client: AsyncClient):
    # 1. Register
    email = "lifecycle@neurodesk.ai"
    password = "SuperPassword2026!"
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Lifecycle Tester", "password": password},
    )
    assert reg_res.status_code == 201

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Get Current User (/users/me)
    me_res = await async_client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 4. Update Profile (/users/profile)
    profile_res = await async_client.put(
        "/api/v1/users/profile",
        headers=headers,
        json={"full_name": "Updated Lifecycle Tester"},
    )
    assert profile_res.status_code == 200
    assert profile_res.json()["full_name"] == "Updated Lifecycle Tester"

    # 5. Token Refresh (/auth/refresh)
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    # 6. Change Password (/users/change-password)
    new_access_token = new_tokens["access_token"]
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    pass_res = await async_client.post(
        "/api/v1/users/change-password",
        headers=new_headers,
        json={"current_password": password, "new_password": "NewSecretPassword2026!"},
    )
    assert pass_res.status_code == 200

    # 7. Logout (/auth/logout)
    logout_res = await async_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
    )
    assert logout_res.status_code == 200

    # 8. Soft Delete Account (/users/delete-account)
    # Login again with new password
    relogin_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "NewSecretPassword2026!"},
    )
    assert relogin_res.status_code == 200
    del_token = relogin_res.json()["access_token"]
    del_res = await async_client.delete(
        "/api/v1/users/delete-account",
        headers={"Authorization": f"Bearer {del_token}"},
    )
    assert del_res.status_code == 200
