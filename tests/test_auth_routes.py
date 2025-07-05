import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    data = {
        "username": "duplicate_user",
        "password_1": "Password1",
        "password_2": "Password1"
    }

    result = await client.post("/auth/register", json=data)
    assert result.status_code == 200


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    data = {
        "username": "duplicate_user",
        "password_1": "Password1",
        "password_2": "Password1"
    }

    result = await client.post("/auth/register", json=data)
    assert result.status_code == 400
    assert result.json()["detail"] == "User with this username already exists"


@pytest.mark.asyncio
async def test_register_invalid_password(client: AsyncClient):
    data = {
        "username": "invalid_user",
        "password_1": "short",
        "password_2": "short"
    }

    result = await client.post("/auth/register", json=data)
    assert result.status_code == 422
    assert result.json()["detail"][0]["msg"] == "Value error, Password must contain at least 1 lowercase, 1 uppercase letter and 1 number, and be between 8 and 64 symbols long"

    data = {
        "username": "invalid_user",
        "password_1": "Password1",
        "password_2": "Password2"
    }
    result = await client.post("/auth/register", json=data)
    assert result.status_code == 422
    assert result.json()["detail"][0]["msg"] == "Value error, Passwords do not match"


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    data = {
        "username": "testuser",
        "password_1": "GoodPass1",
        "password_2": "GoodPass1"
    }

    await client.post("/auth/register", json=data)

    login_data = {
        "username": "testuser",
        "password": "GoodPass1"
    }

    result = await client.post("/auth/login", json=login_data)
    assert result.status_code == 200
    assert "access_token" in result.json()
    assert result.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    login_data = {
        "username": "testuser",
        "password": "WrongPass"
    }

    result = await client.post("/auth/login", json=login_data)
    assert result.status_code == 401
    assert result.json()["detail"] == "Invalid username or password"


@pytest.mark.asyncio
async def test_me_authorized(client: AsyncClient):
    login_data = {
        "username": "testuser",
        "password": "GoodPass1"
    }
    login_result = await client.post("/auth/login", json=login_data)
    token = login_result.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    result = await client.get("/auth/me", headers=headers)
    assert result.status_code == 200
    assert result.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    result = await client.get("/auth/me")
    assert result.status_code == 401
    assert result.json()["detail"] == "Not authenticated"