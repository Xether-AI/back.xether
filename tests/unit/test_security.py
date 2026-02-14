"""Test security utilities."""

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_password_hashing() -> None:
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_access_token_creation() -> None:
    """Test access token creation and decoding."""
    data = {"sub": "user@example.com", "user_id": 1}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user@example.com"
    assert decoded["user_id"] == 1
    assert decoded["type"] == "access"


def test_refresh_token_creation() -> None:
    """Test refresh token creation and decoding."""
    data = {"sub": "user@example.com", "user_id": 1}
    token = create_refresh_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user@example.com"
    assert decoded["user_id"] == 1
    assert decoded["type"] == "refresh"


def test_invalid_token_decoding() -> None:
    """Test decoding invalid token."""
    invalid_token = "invalid.token.here"
    decoded = decode_token(invalid_token)
    assert decoded is None
