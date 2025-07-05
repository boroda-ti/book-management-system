import re

from app.services import auth_service


def test_hash_password_changes_output():
    raw = "MyPass123"
    hashed = auth_service.hash_password(raw)

    assert hashed != raw
    assert isinstance(hashed, str)
    assert bool(re.match(r"^\$2[ab]\$", hashed[:4]))


def test_verify_password():
    password = "MyPass123"
    hash_ = auth_service.hash_password(password)

    assert auth_service.verify_password(password, hash_) is True
    assert auth_service.verify_password("wrongpass", hash_) is False


def test_create_access_token():
    payload = {"sub": "testuser", "user_id": 123}
    token = auth_service.create_access_token(payload)
    decoded = auth_service.decode_access_token(token)

    assert isinstance(token, str)
    assert decoded["sub"] == "testuser"
    assert decoded["user_id"] == 123
    assert "exp" in decoded